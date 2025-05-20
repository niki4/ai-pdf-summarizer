An async PDF document processing application.

Users can upload one or more PDF files via a website. After some time, a per-page content and summarization of these files (one summary per each uploaded file) is displayed on the page. Application accepts any PDF and parses it to a text (or markdown if possible) using one of the following methods:
- PyPDF - this won't extract markdown, only text.
- Google Gemini 2.0 Flash (use its free tier to provision API key) - you can use it for parsing of PDF file to markdown.

The backend takes the uploaded PDF, the desired parser from above, then parses the contents, and finally outputs markdown -formatted text and a summary of that text.

# Set up and run:

## To run the application:
1. First, make sure you have Docker and Docker Compose installed on your system.
2. Create a .env file in the root directory with the content shown below:
```
REDIS_HOST=localhost
REDIS_PORT=6379
GEMINI_API_KEY=<YOUR_API_KEY_HERE>
```
2. Run `docker-compose up --build`
The application will be available at:

* Frontend: http://localhost
* Backend API: http://localhost:8000

The frontend will automatically proxy API requests to the backend service, and the UI will handle:
* File selection and upload
* Processing status display
* Automatic polling for document status
* Display of document content and summary when ready

## If you prefer to test backend only Backend
You can use the following endpoints for testing backend:

1. Upload a PDF:
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test.pdf" \
  -F "parser_type=pypdf"
  ```

2. Retrieve a document (use actual UUID from previous command instead placeholder `{document_id}`):
```bash
curl -X GET "http://localhost:8000/document/{document_id}"
```

# Development

## Backend tests
1. Create & activate venv: `python -m venv .venv` then `.venv\Scripts\activate`
2. Install deps: `pip install -r requirements.txt`
3. Try to run some tests: `pytest app/tests/ -v`

## Frontend tests
1. Make sure you have npm installed: `npm --version`
2. Install deps: `cd frontend && npm install`
3. Run tests: `npm test`

## Tech stack:
- Python 3.12+ with FastAPI
- Redis v7+
- Docker Compose for dependencies like Redis
- PyPDF for simple PDF parsing
- Google Gemini 2.0 Flash for advanced parsing into the markdown and summarization
- Typescript with React for the Frontend
