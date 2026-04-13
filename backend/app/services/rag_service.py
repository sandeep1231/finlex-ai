from app.ai.rag import RAGPipeline


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

    async def add_document(self, file_path: str, category: str = "general") -> int:
        """Add a document to the knowledge base and return chunk count."""
        return await self.pipeline.add_document(file_path, category)

    async def delete_document(self, source_filename: str):
        """Remove a document from the knowledge base."""
        await self.pipeline.delete_document(source_filename)

    async def get_context(self, query: str, mode: str = "general") -> str:
        """Get relevant context from the knowledge base for a query."""
        category = None
        if mode == "accounting":
            category = "tax"
        elif mode == "legal":
            category = "legal"

        results = await self.search(query, k=5, category=category)

        if not results:
            return "No specific context found in the knowledge base."

        context_parts = []
        for doc in results:
            source = doc.metadata.get("source", "unknown")
            context_parts.append(f"[Source: {source}]\n{doc.page_content}")

        return "\n\n---\n\n".join(context_parts)
