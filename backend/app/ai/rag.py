import asyncio
import json
import os
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document as LangchainDocument
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    CSVLoader,
    TextLoader,
    UnstructuredExcelLoader,
)

from app.ai.embeddings import get_embedding_model
from app.config import get_settings

settings = get_settings()

KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent / "knowledge_base"

SUPPORTED_LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".csv": CSVLoader,
    ".txt": TextLoader,
    ".xlsx": UnstructuredExcelLoader,
}


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for Indian accounting and law knowledge."""

    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self.vectorstore: Chroma | None = None

    async def initialize(self):
        """Initialize the vector store and load built-in knowledge base."""
        # Chroma constructor + embeddings are blocking I/O; run in thread pool
        def _init_vectorstore():
            return Chroma(
                persist_directory=settings.chroma_persist_dir,
                embedding_function=self.embedding_model,
                collection_name=settings.chroma_collection_name,
            )
        self.vectorstore = await asyncio.to_thread(_init_vectorstore)

        # Load built-in knowledge base if collection is empty
        collection = self.vectorstore._collection
        if collection.count() == 0:
            await self._load_builtin_knowledge()

    async def _load_builtin_knowledge(self):
        """Load built-in JSON knowledge base files into the vector store."""
        documents = []

        for json_file in KNOWLEDGE_BASE_DIR.rglob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert JSON to readable text documents
            text_content = self._json_to_text(data, json_file.stem)
            category = json_file.parent.name  # tax or legal

            doc = LangchainDocument(
                page_content=text_content,
                metadata={
                    "source": str(json_file.name),
                    "category": category,
                    "type": "builtin_knowledge",
                },
            )
            documents.append(doc)

        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)

        # Add to vector store (blocking I/O with embeddings API)
        if chunks:
            await asyncio.to_thread(self.vectorstore.add_documents, chunks)

    def _json_to_text(self, data: dict, name: str) -> str:
        """Convert a JSON knowledge base file to readable text for embedding."""
        lines = [f"# Knowledge Base: {name.replace('_', ' ').title()}\n"]
        self._flatten_json(data, lines, depth=0)
        return "\n".join(lines)

    def _flatten_json(self, obj, lines: list, depth: int, prefix: str = ""):
        """Recursively flatten JSON into readable text."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                label = key.replace("_", " ").title()
                if isinstance(value, (dict, list)):
                    lines.append(f"{'#' * min(depth + 2, 4)} {prefix}{label}")
                    self._flatten_json(value, lines, depth + 1)
                else:
                    lines.append(f"- **{prefix}{label}**: {value}")
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict):
                    self._flatten_json(item, lines, depth)
                    lines.append("")
                else:
                    lines.append(f"  - {item}")

    async def add_document(self, file_path: str, category: str = "general") -> int:
        """Process and add a user-uploaded document to the vector store."""
        ext = os.path.splitext(file_path)[1].lower()
        loader_class = SUPPORTED_LOADERS.get(ext)

        if not loader_class:
            raise ValueError(f"Unsupported file type: {ext}")

        loader = loader_class(file_path)
        documents = loader.load()

        # Add metadata
        for doc in documents:
            doc.metadata["category"] = category
            doc.metadata["type"] = "user_upload"
            doc.metadata["source"] = os.path.basename(file_path)

        # Split and store (blocking I/O with embeddings API)
        chunks = self.text_splitter.split_documents(documents)
        if chunks:
            await asyncio.to_thread(self.vectorstore.add_documents, chunks)

        return len(chunks)

    async def search(
        self,
        query: str,
        k: int = 5,
        category: str | None = None,
        filter_metadata: dict | None = None,
    ) -> list[LangchainDocument]:
        """Search the knowledge base for relevant documents."""
        search_kwargs = {"k": k}
        if filter_metadata:
            search_kwargs["filter"] = filter_metadata
        elif category:
            search_kwargs["filter"] = {"category": category}

        results = await asyncio.to_thread(
            self.vectorstore.similarity_search_with_relevance_scores,
            query, **search_kwargs
        )

        # Filter by minimum relevance threshold
        filtered = [
            doc for doc, score in results if score >= 0.3
        ]

        return filtered

    async def delete_document(self, source_filename: str):
        """Remove all chunks associated with a document."""
        await asyncio.to_thread(
            self.vectorstore._collection.delete,
            where={"source": source_filename}
        )
