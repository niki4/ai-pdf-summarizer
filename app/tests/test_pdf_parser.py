import pytest
from io import BytesIO
from unittest.mock import Mock, patch
from app.services.pdf_parser import parse_pdf, parse_pdf_with_gemini, generate_summary

# Sample PDF content for testing
SAMPLE_PDF_CONTENT = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"

@pytest.fixture(autouse=True)
def mock_gemini_config():
    """Mock Gemini configuration for all tests"""
    with patch('app.services.pdf_parser.configure_gemini') as mock:
        yield mock

def test_parse_pdf_success():
    """Test successful PDF parsing with PyPDF"""
    with patch('app.services.pdf_parser.PdfReader') as mock_pdf_reader:
        # Mock the PDF reader and its pages
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test content"
        mock_pdf_reader.return_value.pages = [mock_page]

        result = parse_pdf(SAMPLE_PDF_CONTENT)
        
        assert len(result) == 1
        assert result[0] == "Test content"
        mock_pdf_reader.assert_called_once()

def test_parse_pdf_empty_pages():
    """Test PDF parsing with empty pages"""
    with patch('app.services.pdf_parser.PdfReader') as mock_pdf_reader:
        # Mock empty page
        mock_page = Mock()
        mock_page.extract_text.return_value = ""
        mock_pdf_reader.return_value.pages = [mock_page]

        result = parse_pdf(SAMPLE_PDF_CONTENT)
        
        assert len(result) == 0
        mock_pdf_reader.assert_called_once()

def test_parse_pdf_error():
    """Test PDF parsing with invalid content"""
    with pytest.raises(Exception) as exc_info:
        parse_pdf(b"invalid content")
    
    assert "Error parsing PDF" in str(exc_info.value)

@patch('app.services.pdf_parser.get_gemini_model')
def test_parse_pdf_with_gemini_success(mock_get_model):
    """Test successful PDF parsing with Gemini"""
    # Mock Gemini response
    mock_response = Mock()
    mock_response.text = "Page 1 content\n---\nPage 2 content"
    mock_model = Mock()
    mock_model.generate_content.return_value = mock_response
    mock_get_model.return_value = mock_model

    result = parse_pdf_with_gemini(SAMPLE_PDF_CONTENT)
    
    assert len(result) == 2
    assert result[0] == "Page 1 content"
    assert result[1] == "Page 2 content"
    mock_get_model.assert_called_once()

@patch('app.services.pdf_parser.get_gemini_model')
def test_parse_pdf_with_gemini_error(mock_get_model):
    """Test PDF parsing with Gemini when API fails"""
    mock_model = Mock()
    mock_model.generate_content.side_effect = Exception("API Error")
    mock_get_model.return_value = mock_model

    with pytest.raises(Exception) as exc_info:
        parse_pdf_with_gemini(SAMPLE_PDF_CONTENT)
    
    assert "Error parsing PDF with Gemini" in str(exc_info.value)

@patch('app.services.pdf_parser.get_gemini_model')
def test_generate_summary_success(mock_get_model):
    """Test successful summary generation"""
    # Mock Gemini response
    mock_response = Mock()
    mock_response.text = "This is a summary"
    mock_model = Mock()
    mock_model.generate_content.return_value = mock_response
    mock_get_model.return_value = mock_model

    result = generate_summary("Test content to summarize")
    
    assert result == "This is a summary"
    mock_get_model.assert_called_once()

@patch('app.services.pdf_parser.get_gemini_model')
def test_generate_summary_error(mock_get_model):
    """Test summary generation when API fails"""
    mock_model = Mock()
    mock_model.generate_content.side_effect = Exception("API Error")
    mock_get_model.return_value = mock_model

    with pytest.raises(Exception) as exc_info:
        generate_summary("Test content")
    
    assert "Error generating summary" in str(exc_info.value) 