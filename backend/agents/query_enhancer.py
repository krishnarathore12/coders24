from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv

load_dotenv()

query_enhancer = Agent(
    name="Query Enhancer",
    model=Gemini(id="gemini-2.5-flash"), 
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
    markdown=False, 
)