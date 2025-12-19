import os
from agno.knowledge import Knowledge
from agno.vectordb.qdrant import Qdrant
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from dotenv import load_dotenv

load_dotenv()
# --- Configuration ---
# Uses local CPU by default. Change device="cuda" if you have a GPU.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "agni_rag_documents"

def get_knowledge_base() -> Knowledge:
    """
    Returns a configured Agno Knowledge object using env vars for Qdrant.
    """
    # 1. Get Config from Env
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not qdrant_url or not qdrant_api_key:
        raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in the .env file")

    # 2. Initialize Embedder
    embedder = SentenceTransformerEmbedder(
        id=EMBEDDING_MODEL     # <--- Parameter name is now 'id'
    )

    # 3. Initialize Vector DB Connection
    vector_db = Qdrant(
        collection=COLLECTION_NAME,
        url=qdrant_url,
        api_key=qdrant_api_key,  # Authenticated connection
        embedder=embedder,
        distance="cosine"
    )

    # 4. Return Knowledge Base
    return Knowledge(vector_db=vector_db)

# Singleton instance
knowledge_base = get_knowledge_base()