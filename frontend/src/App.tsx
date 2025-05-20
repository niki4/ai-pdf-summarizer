import { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Button, 
  Typography, 
  Paper,
  CircularProgress,
  Alert,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormControl,
  FormLabel,
  Stack
} from '@mui/material';
import axios from 'axios';

interface Document {
  id: string;
  filename: string;
  status: 'queued' | 'completed';
  content?: string[];
  summary?: string;
}

interface UploadResponse {
  document_id: string;
  message: string;
}

interface DocumentResponse {
  status: 'queued' | 'completed';
  timestamp?: string;
  content?: string[];
  summary?: string;
}

type ParserType = 'pypdf' | 'gemini';

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [document, setDocument] = useState<Document | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [parserType, setParserType] = useState<ParserType>('gemini');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
    }
  };

  const handleParserChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setParserType(event.target.value as ParserType);
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('parser_type', parserType);

    try {
      const response = await axios.post<UploadResponse>('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('Upload response:', response.data);
      
      // Initialize document with queued status
      setDocument({
        id: response.data.document_id,
        filename: file.name,
        status: 'queued'
      });
    } catch (err) {
      console.error('Upload error:', err);
      setError('Failed to upload file. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let pollInterval: NodeJS.Timeout;

    const pollDocument = async () => {
      if (!document?.id) return;

      try {
        console.log('Polling document:', document.id);
        const response = await axios.get<DocumentResponse>(`/api/document/${document.id}`);
        console.log('Poll response:', response.data);

        if (response.data.status === 'completed') {
          setDocument(prev => prev ? {
            ...prev,
            status: 'completed',
            content: response.data.content,
            summary: response.data.summary
          } : null);
          // Clear the polling interval when completed
          if (pollInterval) {
            clearInterval(pollInterval);
            console.log('Stopping polling - document completed');
          }
        } else {
          // Keep polling if still queued
          setDocument(prev => prev ? {
            ...prev,
            status: 'queued'
          } : null);
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };

    if (document?.id) {
      console.log('Starting polling for document:', document.id);
      // Poll immediately and then every 2 seconds
      pollDocument();
      pollInterval = setInterval(pollDocument, 2000);
    }

    return () => {
      if (pollInterval) {
        console.log('Cleaning up polling interval');
        clearInterval(pollInterval);
      }
    };
  }, [document?.id]);

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          PDF Document Processor
        </Typography>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
            <Box>
              <input
                accept=".pdf"
                style={{ display: 'none' }}
                id="file-upload"
                type="file"
                onChange={handleFileChange}
              />
              <label htmlFor="file-upload">
                <Button variant="contained" component="span">
                  Select PDF
                </Button>
              </label>
            </Box>
            <Button
              variant="contained"
              color="primary"
              onClick={handleUpload}
              disabled={!file || loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Upload and Summarize PDF'}
            </Button>
          </Stack>

          {file && (
            <Typography sx={{ mb: 2 }}>
              Selected file: {file.name}
            </Typography>
          )}

          <FormControl component="fieldset" sx={{ mb: 2 }}>
            <FormLabel component="legend">Select Parser Type</FormLabel>
            <RadioGroup
              value={parserType}
              onChange={handleParserChange}
            >
              <FormControlLabel 
                value="pypdf" 
                control={<Radio />} 
                label="PyPDF - Extract text only" 
              />
              <FormControlLabel 
                value="gemini" 
                control={<Radio />} 
                label="Google Gemini 2.0 Flash - Extract text and markdown" 
              />
            </RadioGroup>
          </FormControl>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {document && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {document.filename}
            </Typography>
            
            {document.status === 'queued' && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <CircularProgress size={20} />
                <Typography>Processing...</Typography>
              </Box>
            )}

            {document.status === 'completed' && (
              <>
                <Typography variant="h6" sx={{ mt: 2 }} gutterBottom>
                  Summary
                </Typography>
                <Typography paragraph>
                  {document.summary}
                </Typography>

                <Typography variant="h6" sx={{ mt: 2 }} gutterBottom>
                  Content
                </Typography>
                {document.content?.map((page, index) => (
                  <Typography
                    key={index}
                    component="pre"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      wordWrap: 'break-word',
                      backgroundColor: '#f5f5f5',
                      p: 2,
                      borderRadius: 1,
                      mb: 2
                    }}
                  >
                    {page}
                  </Typography>
                ))}
              </>
            )}
          </Paper>
        )}
      </Box>
    </Container>
  );
}

export default App;
