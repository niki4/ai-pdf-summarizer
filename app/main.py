from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
from dotenv import load_dotenv
from .services.pdf_parser import parse_pdf, parse_pdf_with_gemini, generate_summary
from .services.redis_service import RedisService
from .models.parser_type import ParserType

load_dotenv()

app = FastAPI(title="PDF Processing API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Redis service
redis_service = RedisService(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379))
)

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    parser_type: ParserType = ParserType.PYPDF
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        # Read the PDF content
        content = await file.read()
        
        # Parse PDF based on selected parser
        if parser_type == ParserType.PYPDF:
            parsed_content = parse_pdf(content)
        elif parser_type == ParserType.GEMINI:
            parsed_content = parse_pdf_with_gemini(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported parser type")
        
        # Generate summary using Gemini
        summary = generate_summary("\n".join(parsed_content))
        
        # Store results in Redis
        document_id = redis_service.store_document(parsed_content, summary)
        
        return {
            "document_id": document_id,
            "content": parsed_content,
            "summary": summary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/document/{document_id}")
async def get_document(document_id: str):
    document = redis_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document 