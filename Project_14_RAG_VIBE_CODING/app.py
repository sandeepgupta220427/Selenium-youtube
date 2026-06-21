import os
import shutil
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv

# Load valid .env file
load_dotenv()

from rag.ingester import process_file_and_ingest
from rag.generator import generate_answer

app = FastAPI(title="Modular RAG API")

# Add CORS Middleware for potential external UI requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure temp directory for uploads
UPLOAD_DIR = "./temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ChatRequest(BaseModel):
    query: str

@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...), 
    domain: str = Form(...) # 'api', 'ui', or 'perf'
):
    """
    Endpoint for uploading a file to be chunked and indexed into the specified ChromaDB domain.
    """
    if domain not in ["api", "ui", "perf"]:
        raise HTTPException(status_code=400, detail="Invalid domain. Must be 'api', 'ui', or 'perf'.")
        
    temp_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Save file temporarily
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process and Ingest
        chunks_inserted = process_file_and_ingest(temp_path, file.filename, domain)
        
        return {
            "message": "File processed successfully", 
            "filename": file.filename,
            "domain": domain,
            "chunks_inserted": chunks_inserted
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
        
    finally:
        # Cleanup temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/api/chat")
async def chat_query(request: ChatRequest):
    """
    Endpoint for asking the Modular RAG system a question.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    try:
        response = generate_answer(request.query)
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
        
        return response
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")

# Mount the static directory to serve index.html directly from FastAPI
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
