import streamlit as st
import requests

# --- Configuration ---
BACKEND_URL = "http://localhost:8000"  # Pointing to your FastAPI server

st.set_page_config(page_title="Agni RAG", page_icon="🔥")

st.title("🔥 Agni RAG Pipeline")

# --- Sidebar: Document Ingestion ---
with st.sidebar:
    st.header("1. Upload Document")
    st.write("Upload a file to start the RAG context.")
    
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "docx"])
    
    if st.button("Ingest Document"):
        if uploaded_file is not None:
            with st.spinner("Ingesting document..."):
                try:
                    # Preparing the file for the request
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    
                    # NOTE: Adjust the endpoint path below based on your app/ingest.py logic
                    # Assuming the route inside ingest.router is "/upload" or "/"
                    response = requests.post(f"{BACKEND_URL}/api/documents/ingest", files=files)
                    
                    if response.status_code == 200:
                        st.success("Document ingested successfully!")
                    else:
                        st.error(f"Failed to ingest: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
        else:
            st.warning("Please select a file first.")

# --- Main Area: Chat Interface ---
st.header("2. Chat with Agent")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask a question about your documents..."):
    # 1. Display user message
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Call the FastAPI Chat Endpoint
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Based on your ChatRequest pydantic model
                payload = {"message": prompt}
                response = requests.post(f"{BACKEND_URL}/chat", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    bot_reply = data.get("response", "No response received.")
                    
                    # Optional: Show if the query was enhanced (for debugging/transparency)
                    if data.get("enhanced_query"):
                        st.caption(f"✨ Enhanced Query: {data['enhanced_query']}")
                    
                    st.markdown(bot_reply)
                    
                    # Save context
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                else:
                    error_msg = f"Error {response.status_code}: {response.text}"
                    st.error(error_msg)
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to backend. Is main.py running?")