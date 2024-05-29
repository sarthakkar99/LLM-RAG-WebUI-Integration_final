import streamlit as st
import requests

backend_url = "http://localhost:5002"

st.title("LLM Interface with Mode Switching")

if st.button("Refresh Conversation"):
    response = requests.get(f"{backend_url}/get_messages")
    history = response.json()["messages"]
    st.write("### Conversation History")
    for msg_type, msg_content in history:
        if msg_type == "user":
            st.write(f"<div style='color: blue;'>User: {msg_content}</div>", unsafe_allow_html=True)
        else:
            st.write(f"<div style='color: green;'>System: {msg_content}</div>", unsafe_allow_html=True)

if st.button("Refresh RAG Conversation"):
    response = requests.get(f"{backend_url}/get_rag_messages")
    history = response.json()["messages"]
    st.write("### RAG Conversation History")
    for msg_type, msg_content in history:
        if msg_type == "user":
            st.write(f"<div style='color: blue;'>User: {msg_content}</div>", unsafe_allow_html=True)
        else:
            st.write(f"<div style='color: green;'>System: {msg_content}</div>", unsafe_allow_html=True)
