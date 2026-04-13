from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings

from app.config import get_settings

settings = get_settings()


def get_embedding_model():
    """Get the embedding model based on configuration."""
    if settings.llm_provider == "gemini":
        return GoogleGenerativeAIEmbeddings(
            model=settings.embedding_model,
            google_api_key=settings.google_api_key,
        )
    elif settings.llm_provider == "openai":
        return OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )
    else:
        return OllamaEmbeddings(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
        )
