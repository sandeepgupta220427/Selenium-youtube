# Local ChromaDB Viewer

This is a local Streamlit application to visualize and explore the ChromaDB collections used by the Modular RAG system.

## Setup

Ensure you have installed the project requirements from the main directory:

```bash
cd ..
pip install -r requirements.txt
```

*(Note: `streamlit` and `pandas` must be installed.)*

## Running the Viewer

To run the viewer, navigate to this directory and run:

```bash
streamlit run app.py
```

The application will launch in your default web browser, allowing you to browse the local `chroma_db` database.
