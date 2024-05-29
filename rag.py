import requests
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
import os

def process_rag(pdf_link, question):
    try:
        if pdf_link.startswith("http://") or pdf_link.startswith("https://"):
            # Download the PDF document
            response = requests.get(pdf_link)
            pdf_path = "temp.pdf"
            with open(pdf_path, "wb") as f:
                f.write(response.content)
        else:
            # Use the local file path
            pdf_path = pdf_link

        # Load PDF content using PyPDFLoader
        loader = PyPDFLoader(pdf_path)
        text_documents = loader.load()

        # Split text into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        documents = text_splitter.split_documents(text_documents)

        # Create vector store from document embeddings
        db = Chroma.from_documents(documents[:20], OllamaEmbeddings())

        # Perform similarity search based on the question
        retrieved_results = db.similarity_search(question)
        
        if retrieved_results:
            return retrieved_results[0].page_content
        else:
            return "No relevant information found."
    except Exception as e:
        return f"An error occurred: {e}"
