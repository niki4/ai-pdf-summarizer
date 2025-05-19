from io import BytesIO
from pypdf import PdfReader

def parse_pdf(content: bytes) -> str:
    """
    Parse PDF content using PyPDF and return the extracted text.
    
    Args:
        content (bytes): The PDF file content in bytes
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        pdf_file = BytesIO(content)
        pdf_reader = PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
            
        return text.strip()
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}") 