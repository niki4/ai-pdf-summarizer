from io import BytesIO
from pypdf import PdfReader
import google.generativeai as genai
import os
import base64
from typing import List
import logging

logger = logging.getLogger(__name__)

def configure_gemini():
    """Configure Gemini API with the API key"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    genai.configure(api_key=api_key)

# Configure Gemini only when the module is actually used
def get_gemini_model():
    """Get configured Gemini model"""
    configure_gemini()
    return genai.GenerativeModel('gemini-2.0-flash')

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

def parse_pdf_with_gemini(content: bytes) -> List[str]:
    """
    Parse PDF content using Google Gemini 2.0 Flash and return the extracted text in markdown format.

    Args:
        content (bytes): The PDF file content in bytes

    Returns:
        List[str]: List of markdown-formatted text for each page
    """
    try:
        # Convert PDF content to base64
        pdf_base64 = base64.b64encode(content).decode('utf-8')

        # Use Gemini to process the PDF and convert to markdown
        model = get_gemini_model()
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
        logger.info("Initializing Gemini model for summary generation")
        model = get_gemini_model()
        logger.info("Generating summary")
        response = model.generate_content(f"Please provide a concise summary of the following text:\n\n{text}")
        logger.info("Summary generated successfully")
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error in generate_summary: {str(e)}", exc_info=True)
        raise Exception(f"Error generating summary: {str(e)}")
