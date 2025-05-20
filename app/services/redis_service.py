import json
import uuid
import logging
from redis import Redis
from typing import List, Union, Dict, Optional
import time

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self, host: str = "localhost", port: int = 6379):
        logger.info(f"Initializing Redis service with host={host}, port={port}")
        
        # Redis connection for text data (streams, status, etc.)
        self.redis = Redis(host=host, port=port, decode_responses=True)
        # Redis connection for binary data (PDF content)
        self.redis_binary = Redis(host=host, port=port, decode_responses=False)
        
        # Test connections
        try:
            self.redis.ping()
            self.redis_binary.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
        
        self.stream_key = "document_processing"
        self.group_name = "document_processors"
        self.consumer_name = "processor_1"
        
        # Create consumer group if it doesn't exist
        try:
            self.redis.xgroup_create(self.stream_key, self.group_name, mkstream=True)
            logger.info(f"Created consumer group {self.group_name} for stream {self.stream_key}")
        except Exception as e:
            logger.info(f"Consumer group {self.group_name} might already exist: {str(e)}")
        
    def queue_document(self, content: bytes, parser_type: str) -> str:
        """
        Queue a document for processing using Redis Streams.
        
        Args:
            content (bytes): The PDF file content in bytes
            parser_type (str): The type of parser to use
            
        Returns:
            str: The generated document ID
        """
        document_id = str(uuid.uuid4())
        logger.info(f"Queueing document {document_id} for processing")
        
        try:
            # Store the document content temporarily using binary connection
            self.redis_binary.setex(
                f"temp_doc:{document_id}",
                3600,  # 1 hour expiration
                content
            )
            
            # Add to processing stream using text connection
            stream_id = self.redis.xadd(
                self.stream_key,
                {
                    "document_id": document_id,
                    "parser_type": parser_type,
                    "status": "queued",
                    "timestamp": str(time.time())
                }
            )
            logger.info(f"Added document {document_id} to stream with ID {stream_id}")
            
            return document_id
        except Exception as e:
            logger.error(f"Error queueing document: {str(e)}", exc_info=True)
            raise
    
    def get_document_status(self, document_id: str) -> Dict:
        """
        Get the current status of a document.
        
        Args:
            document_id (str): The document ID to check
            
        Returns:
            Dict: Document status information
        """
        try:
            # First check if document is processed
            document = self.get_document(document_id)
            if document:
                return {
                    "status": "completed",
                    "content": document["content"],
                    "summary": document["summary"]
                }
            
            # If not processed, check stream for status
            stream_entries = self.redis.xrange(self.stream_key)
            for entry_id, entry in stream_entries:
                if entry.get("document_id") == document_id:
                    status = entry.get("status", "queued")
                    return {
                        "status": status,
                        "timestamp": entry.get("timestamp")
                    }
            
            # If not found in stream or processed documents, return not found
            return {"status": "not_found"}
            
        except Exception as e:
            logger.error(f"Error getting document status: {str(e)}", exc_info=True)
            raise
    
    def store_document(self, document_id: str, content: Union[str, List[str]], summary: str) -> None:
        """
        Store processed document content and summary in Redis.
        
        Args:
            document_id (str): The document ID
            content (Union[str, List[str]]): The parsed text from the PDF
            summary (str): The generated summary
        """
        try:
            logger.info(f"Storing processed document {document_id}")
            document_data = {
                "content": content,
                "summary": summary
            }
            
            # Store the processed document
            self.redis.set(
                f"document:{document_id}",
                json.dumps(document_data)
            )
            
            # Find and update the stream entry
            stream_entries = self.redis.xrange(self.stream_key)
            for entry_id, entry in stream_entries:
                if entry.get("document_id") == document_id:
                    # Update the existing entry with completed status
                    self.redis.xdel(self.stream_key, entry_id)
                    self.redis.xadd(
                        self.stream_key,
                        {
                            "document_id": document_id,
                            "status": "completed",
                            "timestamp": str(time.time())
                        }
                    )
                    # Clean up temporary document
                    self.redis_binary.delete(f"temp_doc:{document_id}")
                    logger.info(f"Updated status to completed for document {document_id}")
                    break
            
        except Exception as e:
            logger.error(f"Error storing document: {str(e)}", exc_info=True)
            raise
    
    def get_document(self, document_id: str) -> Optional[dict]:
        """
        Retrieve document content and summary from Redis.
        
        Args:
            document_id (str): The document ID to retrieve
            
        Returns:
            Optional[dict]: The document data containing parsed text and summary
        """
        try:
            data = self.redis.get(f"document:{document_id}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}", exc_info=True)
            raise
    
    def get_next_document(self) -> Optional[tuple]:
        """
        Get the next document to process from the stream.
        
        Returns:
            Optional[tuple]: Tuple of (entry_id, document_id, parser_type, content)
        """
        try:
            # Read from stream with blocking
            entries = self.redis.xreadgroup(
                self.group_name,
                self.consumer_name,
                {self.stream_key: ">"},
                count=1,
                block=1000
            )
            
            if not entries:
                return None
                
            for stream, stream_entries in entries:
                for entry_id, entry in stream_entries:
                    if entry.get("status") == "queued":
                        document_id = entry.get("document_id")
                        parser_type = entry.get("parser_type")
                        
                        # Get document content using binary connection
                        content = self.redis_binary.get(f"temp_doc:{document_id}")
                        if content:
                            logger.info(f"Found document {document_id} to process")
                            return entry_id, document_id, parser_type, content
                        else:
                            logger.error(f"Document content not found for {document_id}")
                            
            return None
        except Exception as e:
            logger.error(f"Error reading from stream: {str(e)}", exc_info=True)
            return None
    
    def acknowledge_processing(self, entry_id: str) -> None:
        """
        Acknowledge that a document has been processed.
        
        Args:
            entry_id (str): The stream entry ID to acknowledge
        """
        try:
            self.redis.xack(self.stream_key, self.group_name, entry_id)
            logger.info(f"Acknowledged processing of entry {entry_id}")
        except Exception as e:
            logger.error(f"Error acknowledging entry {entry_id}: {str(e)}", exc_info=True)
            raise
