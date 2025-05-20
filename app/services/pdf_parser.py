from io import BytesIO
from pypdf import PdfReader
import google.generativeai as genai
import os
import base64
from typing import List

def parse_pdf(content: bytes) -> List[str]:
    """
    Parse PDF content using PyPDF and return the extracted text per page.
    
    Args:
        content (bytes): The PDF file content in bytes
        
    Returns:
        List[str]: List of extracted text from each page of the PDF
    """
    try:
        pdf_file = BytesIO(content)
        pdf_reader = PdfReader(pdf_file)
        
        pages = []
        for page in pdf_reader.pages:
            text = page.extract_text().strip()
            if text:  # Only add non-empty pages
                pages.append(text)
            
        return pages
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")

def parse_pdf_with_gemini(content: bytes) -> list[str]:
    """
    Parse PDF content using Google Gemini 2.0 Flash and return the extracted text in markdown format.
    
    Args:
        content (bytes): The PDF file content in bytes
        
    Returns:
        list[str]: List of markdown-formatted text for each page
    """
    try:
        # Convert PDF content to base64
        pdf_base64 = base64.b64encode(content).decode('utf-8')
        
        # Use Gemini to process the PDF and convert to markdown
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""Please analyze this PDF and convert its content into well-formatted markdown.
        Process each page separately and preserve all important information, structure, and formatting.
        Include headers, lists, and other markdown elements where appropriate.
        Return the content as a list of markdown-formatted text for each page.
        
        PDF content (base64):
        {pdf_base64}
        """
        
        response = model.generate_content(prompt)
        # Split the response into pages (assuming pages are separated by "---" or similar markers)
        pages = [page.strip() for page in response.text.split("---") if page.strip()]
        return pages
    except Exception as e:
        raise Exception(f"Error parsing PDF with Gemini: {str(e)}")

def generate_summary(text: str) -> str:
    """
    Generate a summary of the given text using Gemini.
    
    Args:
        text (str): The text to summarize
        
    Returns:
        str: Generated summary
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(f"Please provide a concise summary of the following text:\n\n{text}")
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Error generating summary: {str(e)}") 