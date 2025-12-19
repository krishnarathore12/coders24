from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv

load_dotenv()

# Define the Query Enhancer Agent
query_enhancer = Agent(
    name="Query Enhancer",
    model=Gemini(id="gemini-2.5-flash"), # Fast model is best for this step
    description="I am an expert at refining search queries for vector databases.",
    instructions=[
        "You are a Query Rewriting Engine for a RAG (Retrieval Augmented Generation) system.",
        "Your goal is to rewrite the user's raw input into a clear, semantic search query.",
        "Rules:",
        "1. Remove conversational filler (e.g., 'Hello', 'Please').",
        "2. Expand ambiguous terms or acronyms if the context is obvious.",
        "3. Focus on keywords that would likely appear in technical documentation.",
        "4. Output ONLY the rewritten query. Do not add explanations.",
    ],
    markdown=False, # We want raw text output
)

# Example Usage Function
def get_enhanced_query(user_input: str) -> str:
    """
    Takes a raw user input and returns the enhanced query string.
    """
    response = query_enhancer.run(user_input)
    return response.content

# --- Testing the Agent ---
if __name__ == "__main__":
    raw_query = "code not working in main.py what do"
    
    print(f"Original: {raw_query}")
    enhanced = get_enhanced_query(raw_query)
    print(f"Enhanced: {enhanced}")