import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from agno.knowledge import Knowledge
from agno.vectordb.qdrant import Qdrant
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder
from agno.knowledge.reranker.cohere import CohereReranker

load_dotenv()

qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
cohere_api_key = os.getenv("COHERE_API_KEY") 
google_api_key = os.getenv("GOOGLE_API_KEY")

collection_name = "agni-rag-documents"

embedder = SentenceTransformerEmbedder()
reranker = CohereReranker(
    model="rerank-english-v3.0", 
    api_key=cohere_api_key,
    top_n=5
)

vector_db = Qdrant(
    collection=collection_name,
    url=qdrant_url,
    api_key=qdrant_api_key,
    embedder=embedder, 
    reranker=reranker,
)

knowledge_base = Knowledge(
    vector_db=vector_db,
    max_results=20,
)

query_responser = Agent(
    name="Query Responser",
    model=Gemini(id="gemini-2.5-flash", api_key=google_api_key), 
    knowledge=knowledge_base,
    search_knowledge=True,
    description="I am an intelligent assistant designed to answer user queries accurately by retrieving and analyzing information from the provided knowledge base.",
    instructions=[
        "Always search the knowledge base for every user query.",
        "Formulate your answer based strictly on the retrieved context.",
        "If the answer is found in the knowledge base, provide a clear and concise response, citing the source document or section where possible.",
        "If the answer is NOT in the knowledge base, clearly state that the information is unavailable in the provided documents.",
        "Do not hallucinate or add external information not found in the context."
    ],
    markdown=True, 
    debug_mode=True
)

def get_response(user_input: str) -> str:
    """
    Takes a raw user input, searches the knowledge base, 
    and returns the RAG-enhanced response.
    """
    response = query_responser.run(user_input)
    return response.content

# --- Testing the Agent ---
if __name__ == "__main__":
    print("Loading knowledge base...")
    # This will now use Sentence Transformers to embed the PDF content
    # knowledge_base.load(recreate=False) 
    
    knowledge_base.add_content(
        url="https://arxiv.org/pdf/2512.16916"
    )
    
    raw_query = "what is gravitational waveforms"
    
    print("-" * 50)
    print(f"User Query: {raw_query}")
    print("-" * 50)
    
    enhanced_response = get_response(raw_query)
    
    print("-" * 50)
    print("RAG Response:")
    print(enhanced_response)