from enum import Enum

class ParserType(str, Enum):
    PYPDF = "pypdf"
    GEMINI = "gemini"
    MISTRAL = "mistral" 