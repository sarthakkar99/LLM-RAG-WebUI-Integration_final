

# Initialize environment variables
import requests
from flask import Flask, jsonify, request
import threading
import logging
import subprocess
import sys
from langchain.prompts import PromptTemplate
from langchain.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import speech_recognition as sr
from gtts import gTTS
import pygame
import subprocess
import re
import os
from rag import process_rag


load_dotenv()

app = Flask(__name__)

# Initialize components for LangChain
template = "You are a helpful assistant. Please respond to the queries. Question: {question}"
prompt = PromptTemplate(input_variables=["question"], template=template)
llm = Ollama(model="llama2")
output_parser = StrOutputParser()

# Lists to store conversation history and RAG mode data
conversation_context = []
current_mode = "chat"
rag_context = []
pdf_link = None

def handle_llm_query(query):
    response = llm(query)
    parsed_response = output_parser.parse(response)
    return parsed_response

@app.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify({"messages": conversation_context})

@app.route('/get_rag_messages', methods=['GET'])
def get_rag_messages():
    return jsonify({"messages": rag_context})

@app.route('/query', methods=['POST'])
def handle_query():
    global current_mode, conversation_context, rag_context, pdf_link
    data = request.json
    user_input = data.get('query')

    if "switch to RAG mode" in user_input:
        current_mode = "RAG"
        return jsonify({"response": "Switched to RAG mode. Please enter the PDF file link."})
    elif "switch to chat mode" in user_input:
        current_mode = "chat"
        pdf_link = None
        return jsonify({"response": "Switched to chat mode."})

    conversation_context.append(("user", user_input))

    if current_mode == "RAG":
        if pdf_link is None:
            pdf_link = user_input
            rag_context.append(("system", f"PDF file link received: {pdf_link}. You can now ask questions related to this document."))
            return jsonify({"response": "PDF file link received. You can now ask questions related to this document."})
        else:
            response = process_rag(pdf_link, user_input)
    else:
        response = handle_llm_query(user_input)

    conversation_context.append(("system", response))

    # Forward the conversation to Streamlit for display
    try:
        requests.post("http://localhost:8501/_stcore/update_session_state", json={'conversation_context': conversation_context})
    except Exception as e:
        print(f"Failed to update Streamlit session state: {e}")

    return jsonify({"response": response})

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(conversation_context)

def input_thread():
    global conversation_context
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        user_query = input("Enter your query (or 'audio' to switch to audio input): ").strip()

        if user_query.lower() == "audio":
            print("Listening for audio input...")
            with mic as source:
                audio = recognizer.listen(source)
            try:
                user_query = recognizer.recognize_google(audio)
                print(f"Recognized query: {user_query}")
            except sr.UnknownValueError:
                print("Could not understand audio")
                continue
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                continue

        conversation_context.append(("user", user_query))
        payload = {"query": user_query}
        response = requests.post("http://localhost:5002/query", json=payload).json()
        print("response: " + response['response'])
        conversation_context.append(("system", response['response']))

def stt_thread():
    # Start subprocess to run Streamlit app
    stt = subprocess.Popen(["streamlit", "run", "streamlit_app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = stt.communicate()
    print(stdout.decode())
    print(stderr.decode())

if __name__ == '__main__':
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)
    
    input_thread = threading.Thread(target=input_thread)
    input_thread.daemon = True
    input_thread.start()

    stt_thread = threading.Thread(target=stt_thread)
    stt_thread.daemon = True
    stt_thread.start()

    app.run(port=5002)