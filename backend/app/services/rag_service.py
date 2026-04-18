import re

from app.ai.rag import RAGPipeline

# Patterns that indicate the user is asking about their uploaded documents
_DOCUMENT_QUERY_RE = re.compile(
    r"\b(upload|document|pdf|file|attachment|analyse|analyze|summarize|summarise|summary|my\s+doc)",
    re.IGNORECASE,
)


class RAGService:
    """Service layer wrapping the RAG pipeline for the application."""

    def __init__(self):
        self.pipeline = RAGPipeline()

    async def initialize(self):
        """Initialize the RAG pipeline and load knowledge base."""
        await self.pipeline.initialize()

    async def search(self, query: str, k: int = 5, category: str | None = None):
        """Search the knowledge base."""
        return await self.pipeline.search(query, k=k, category=category)

    async def search_uploads(self, query: str, k: int = 5):
        """Search only user-uploaded documents."""
        return await self.pipeline.search(query, k=k, filter_metadata={"type": "user_upload"})

    async def add_document(self, file_path: str, category: str = "general") -> int:
        """Add a document to the knowledge base and return chunk count."""
        return await self.pipeline.add_document(file_path, category)

    async def delete_document(self, source_filename: str):
        """Remove a document from the knowledge base."""
        await self.pipeline.delete_document(source_filename)

    async def get_context(self, query: str, mode: str = "general") -> str:
        """Get relevant context from the knowledge base for a query."""
        is_doc_query = bool(_DOCUMENT_QUERY_RE.search(query))

        if is_doc_query:
            # User is asking about an uploaded document — search uploads first
            upload_results = await self.search_uploads(query, k=5)
            # Also do a general search but with fewer results
            general_results = await self.search(query, k=3, category=None)
            # Combine: uploaded docs first (deduplicated)
            seen_content = {doc.page_content[:100] for doc in upload_results}
            for doc in general_results:
                if doc.page_content[:100] not in seen_content:
                    upload_results.append(doc)
                    seen_content.add(doc.page_content[:100])
            results = upload_results
        else:
            results = await self.search(query, k=5, category=None)

        if not results:
            if is_doc_query:
                return "No uploaded documents found. The user may not have uploaded any documents yet."
            return "No specific context found in the knowledge base or uploaded documents."

        context_parts = []
        for doc in results:
            source = doc.metadata.get("source", "unknown")
            doc_type = doc.metadata.get("type", "built-in")
            label = f"[Uploaded Document: {source}]" if doc_type == "user_upload" else f"[Knowledge Base: {source}]"
            context_parts.append(f"{label}\n{doc.page_content}")

        return "\n\n---\n\n".join(context_parts)
