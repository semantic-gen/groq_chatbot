import streamlit as st
from groq import Groq

# Page configuration
st.set_page_config(page_title="Groq Chatbot", page_icon="💬", layout="centered")

# Title
st.title("💬 Groq AI Chatbot")

# Initialize Groq client
@st.cache_resource
def get_groq_client():
    # Try to get API key from secrets first, then environment variable
    import os
    api_key = st.secrets.get("GROQ_API_KEY", None) or os.getenv("GROQ_API_KEY")

    
    if not api_key:
        st.error("⚠️ Please set GROQ_API_KEY environment variable or in Streamlit secrets")
        st.info("Get your API key from: https://console.groq.com")
        st.stop()
    return Groq(api_key=api_key)

client = get_groq_client()

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Stream response from Groq (all models below are FREE)
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Free model - best quality
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                max_tokens=1024,
                temperature=0.7
            )
            
            # Display streaming response
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            full_response = f"Error: {str(e)}"
            message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Sidebar with options
with st.sidebar:
    st.header("Settings")
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This chatbot uses Groq AI's fast inference API with the Llama 3.3 70B model.")
    st.markdown("### Available FREE Models")
    st.markdown("""
    - llama-3.3-70b-versatile ⭐
    - llama-3.1-70b-versatile
    - llama-3.1-8b-instant (fastest)
    - mixtral-8x7b-32768
    - gemma2-9b-it
    
    All models are completely free!
    """)