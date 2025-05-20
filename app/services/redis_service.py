import json
import uuid
from redis import Redis
from typing import List, Union

class RedisService:
    def __init__(self, host: str = "localhost", port: int = 6379):
        self.redis = Redis(host=host, port=port, decode_responses=True)
        
    def store_document(self, content: Union[str, List[str]], summary: str) -> str:
        """
        Store document content and summary in Redis.
        
        Args:
            content (Union[str, List[str]]): The parsed text from the PDF (either plain text or list of markdown pages)
            summary (str): The generated summary
            
        Returns:
            str: The generated document ID
        """
        document_id = str(uuid.uuid4())
        document_data = {
            "content": content,
            "summary": summary
        }
        
        self.redis.set(
            f"document:{document_id}",
            json.dumps(document_data)
        )
        
        return document_id
    
    def get_document(self, document_id: str) -> dict:
        """
        Retrieve document content and summary from Redis.
        
        Args:
            document_id (str): The document ID to retrieve
            
        Returns:
            dict: The document data containing parsed text and summary
        """
        data = self.redis.get(f"document:{document_id}")
        if data:
            return json.loads(data)
        return None
