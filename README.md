The task

An async document processing application. Users can upload one or more PDF files via a website that you'll create. After some time, a per-page content and summarization of these files (one summary per each uploaded file) is displayed on the page. Application accepts any PDF and parses it to a text (or markdown if possible) using one of the following methods (allow user to choose between those methods):
- PyPDF - this won't extract markdown, only text, but that's fine.
- Google Gemini 2.0 Flash (use its free tier to provision API key) - you can use it for parsing of PDF file to markdown


The backend takes the uploaded PDF, the desired parser from above, then parses the contents, and finally outputs markdown -formatted text and a summary of that text.

Tech stack used:
- Python 3.12+ with FastAPI
- Redis v7+
- Docker Compose for dependencies like Redis
- PyPDF for simple PDF parsing
- Google Gemini 2.0 Flash for advanced parsing into the markdown and summarization
- Javascript or Typescript with React (or Next.JS) for the Frontend

Implementation details:
- Start with the backend part, we're less interested in Frontend (nice to have, but not a must).
- The API should take the uploaded PDF, and the desired parser value - PyPDF, Google Gemini Flash or Mistral - and then parse and store in Redis the resulting markdown and a summary of that text.
- For the summary just use Gemini Flash 2.0.
- It is acceptable to demo your application using Postman or CURL instead of full frontend, if you didn't have time to complete it.
- Use Redis Streams feature of Redis as a queue to asynchronously process uploaded documents
- You can use any public PDFs of your choice as a sample to demo
- On Frontend you can use API polling, websockets or SSE to display summarization results once they're ready (but ok to demo with Postman or CURL).


Helpful:
- Google Gemini MODEL_ID = "gemini-2.0-flash" and some examples of usage can be found here https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/getting-started/intro_gemini_2_0_flash.ipynb
- If some requirements are not clear, then make reasonable assumptions and move forward with implementation
- If you stuck on some technicality then feel free to work around it any way you can, and proceed forward with implementation


The priority of implemented features (top to bottom: from most important to "nice to have"):
- Backend application, able to run and serve concurrent API requests
- Document upload and processing with PyPDF
- Async Redis queue with Streams
- Summarization via Google Gemini
- Document processing via Mistral OCR
- Frontend

--
Set up and run:

1. irst, make sure you have Docker and Docker Compose installed on your system.
2. Create a .env file in the root directory with the content shown above. Replace `your_GEMINI_API_KEY_here` with your actual Google Gemini API key.
3. Build and start the services using Docker Compose: `docker-compose up --build`
The application will be available at http://localhost:8000. You can use the following endpoints:

1. Upload a PDF:
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_file.pdf" \
  -F "parser_type=pypdf"
  ```

2. Retrieve a document:
```bash
curl -X GET "http://localhost:8000/document/{document_id}"
```

