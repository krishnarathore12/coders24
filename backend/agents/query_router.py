from agno.agent import Agent
from agno.models.google import Gemini
import os
from dotenv import load_dotenv

load_dotenv()

# The context against which we are routing
doc_summary = "research paper content related or finance related content"

# Define the Router Agent
router_agent = Agent(
    name="Query Router",
    # utilizing a fast model for classification
    model=Gemini(id="gemini-2.5-flash"), 
    description="You are a strict query router.",
    instructions=[
        f"You have access to the following document summary: '{doc_summary}'",
        "Your goal is to determine if the user's query is relevant to this summary.",
        "RULES:",
        "1. If the query is related to the summary, output exactly: 'yes'",
        "2. If the query is unrelated, output exactly: 'no'",
        "3. Do not output markdown, explanations, or punctuation. Just the word."
    ],
    markdown=False, 
)

def route_query(user_input: str) -> str:
    """
    Takes a raw user input and returns 'yes' or 'no'.
    """
    response = router_agent.run(user_input)
    # .strip() removes any accidental whitespace/newlines
    return response.content.strip().lower() 

# --- Testing the Agent ---
if __name__ == "__main__":
    # Test Case 1: Irrelevant query
    query_1 = "How do I bake a chocolate cake?"
    decision_1 = route_query(query_1)
    print(f"Query: {query_1}")
    print(f"Route: {decision_1}") # Should print: no
    
    print("-" * 20)

    # Test Case 2: Relevant query
    query_2 = "What is the difference between supervised and unsupervised learning?"
    decision_2 = route_query(query_2)
    print(f"Query: {query_2}")
    print(f"Route: {decision_2}") # Should print: yes