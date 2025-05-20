import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import axios from 'axios';
import App from './App';

// Mock axios
vi.mock('axios');
const mockedAxios = axios as unknown as jest.Mocked<typeof axios>;

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the main heading', () => {
    render(<App />);
    expect(screen.getByText('PDF Document Processor')).toBeInTheDocument();
  });

  it('renders file upload button', () => {
    render(<App />);
    expect(screen.getByText('Select PDF')).toBeInTheDocument();
  });

  it('renders upload and summarize button', () => {
    render(<App />);
    expect(screen.getByText('Upload and Summarize PDF')).toBeInTheDocument();
  });

  it('displays selected file name after file selection', async () => {
    render(<App />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/select pdf/i);
    
    await userEvent.upload(input, file);
    
    expect(screen.getByText('Selected file: test.pdf')).toBeInTheDocument();
  });

  it('handles file upload successfully', async () => {
    const mockUploadResponse = {
      data: {
        document_id: '123',
        message: 'File uploaded successfully'
      }
    };
    
    mockedAxios.post.mockResolvedValueOnce(mockUploadResponse);
    
    render(<App />);
    
    // Select file
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/select pdf/i);
    await userEvent.upload(input, file);
    
    // Click upload button
    const uploadButton = screen.getByText('Upload and Summarize PDF');
    await userEvent.click(uploadButton);
    
    // Verify axios was called with correct parameters
    expect(mockedAxios.post).toHaveBeenCalledWith(
      '/api/upload',
      expect.any(FormData),
      expect.any(Object)
    );
  });

  it('handles file upload error', async () => {
    mockedAxios.post.mockRejectedValueOnce(new Error('Upload failed'));
    
    render(<App />);
    
    // Select file
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/select pdf/i);
    await userEvent.upload(input, file);
    
    // Click upload button
    const uploadButton = screen.getByText('Upload and Summarize PDF');
    await userEvent.click(uploadButton);
    
    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText('Failed to upload file. Please try again.')).toBeInTheDocument();
    });
  });

  it('changes parser type when radio button is clicked', async () => {
    render(<App />);
    
    // Default should be 'gemini'
    expect(screen.getByLabelText('Google Gemini 2.0 Flash - Extract text and markdown')).toBeChecked();
    
    // Click PyPDF option
    const pypdfRadio = screen.getByLabelText('PyPDF - Extract text only');
    await userEvent.click(pypdfRadio);
    
    expect(pypdfRadio).toBeChecked();
  });

  it('polls for document status after successful upload', async () => {
    const mockUploadResponse = {
      data: {
        document_id: '123',
        message: 'File uploaded successfully'
      }
    };
    
    const mockPollResponse = {
      data: {
        status: 'completed',
        content: ['Page 1 content'],
        summary: 'Document summary'
      }
    };
    
    mockedAxios.post.mockResolvedValueOnce(mockUploadResponse);
    mockedAxios.get.mockResolvedValueOnce(mockPollResponse);
    
    render(<App />);
    
    // Select and upload file
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/select pdf/i);
    await userEvent.upload(input, file);
    
    const uploadButton = screen.getByText('Upload and Summarize PDF');
    await userEvent.click(uploadButton);
    
    // Wait for polling to complete
    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/document/123');
    });
  });
}); 