import os
import shutil
import tempfile
from typing import List

import pandas as pd
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Initialize the embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Collection mapping
COLLECTIONS = {
    "api": "api_docs",
    "ui": "ui_docs",
    "perf": "perf_docs"
}

# Chroma path
PERSIST_DIRECTORY = "./chroma_db"

def get_vector_store(domain: str) -> Chroma:
    """Returns the ChromaDB vector store instance for a specific domain."""
    collection_name = COLLECTIONS.get(domain)
    if not collection_name:
        raise ValueError(f"Invalid domain classification: {domain}. Must be one of {list(COLLECTIONS.keys())}")
        
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

def extract_text_from_csv(file_path: str) -> str:
    """Extracts text from a CSV file."""
    df = pd.read_csv(file_path)
    return df.to_string()

def process_file_and_ingest(file_path: str, filename: str, domain: str) -> int:
    """
    Extracts text based on file type, chunks it, and ingests it into ChromaDB.
    Returns the number of chunks ingested.
    """
    ext = os.path.splitext(filename)[1].lower()
    text = ""
    
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext == ".csv":
        text = extract_text_from_csv(file_path)
    elif ext in [".txt", ".md"]:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    if not text.strip():
        raise ValueError("No text extracted from the document.")

    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    
    # We create raw Document-like objects manually to pass to Chroma `add_texts`
    chunks = text_splitter.split_text(text)
    
    # Metadata for each chunk
    metadatas = [{"source": filename, "domain": domain} for _ in range(len(chunks))]
    
    # Ingest into appropriate database
    vector_store = get_vector_store(domain)
    vector_store.add_texts(texts=chunks, metadatas=metadatas)
    
    return len(chunks)
