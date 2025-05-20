import os
import logging
from dotenv import load_dotenv
from .services.redis_service import RedisService
from .services.pdf_parser import parse_pdf, parse_pdf_with_gemini, generate_summary
from .models.parser_type import ParserType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def process_documents():
    """
    Background worker that processes documents from the Redis Stream.
    """
    logger.info("Starting document processing worker")
    
    redis_service = RedisService(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379))
    )
    
    logger.info(f"Connected to Redis at {os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', '6379')}")
    
    while True:
        try:
            # Get next document to process
            logger.info("Waiting for next document to process...")
            result = redis_service.get_next_document()
            
            if not result:
                logger.debug("No documents in queue")
                continue
                
            entry_id, document_id, parser_type, content = result
            logger.info(f"Processing document {document_id} with parser {parser_type}")
            
            try:
                # Parse document based on parser type
                if parser_type == ParserType.PYPDF:
                    logger.info(f"Using PyPDF parser for document {document_id}")
                    parsed_content = parse_pdf(content)
                elif parser_type == ParserType.GEMINI:
                    logger.info(f"Using Gemini parser for document {document_id}")
                    parsed_content = parse_pdf_with_gemini(content)
                else:
                    raise ValueError(f"Unsupported parser type: {parser_type}")
                
                logger.info(f"Successfully parsed document {document_id}")
                
                # Generate summary
                logger.info(f"Generating summary for document {document_id}")
                summary = generate_summary("\n".join(parsed_content))
                logger.info(f"Summary generated for document {document_id}")
                
                # Store processed document
                logger.info(f"Storing processed document {document_id}")
                redis_service.store_document(document_id, parsed_content, summary)
                
                # Acknowledge processing
                logger.info(f"Acknowledging processing of document {document_id}")
                redis_service.acknowledge_processing(entry_id)
                
                logger.info(f"Successfully processed document {document_id}")
                
            except Exception as e:
                logger.error(f"Error processing document {document_id}: {str(e)}", exc_info=True)
                continue
                
        except Exception as e:
            logger.error(f"Worker error: {str(e)}", exc_info=True)
            continue

if __name__ == "__main__":
    process_documents() 