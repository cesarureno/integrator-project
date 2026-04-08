from pydantic import BaseModel, Field
from typing import List, Optional

class SentimentAnalysis(BaseModel):
    """Result of sentiment analysis on a piece of text."""
    sentiment: str = Field(description="The sentiment of the text (e.g., positive, negative, neutral)")
    score: float = Field(description="A confidence score between 0 and 1")
    keywords: List[str] = Field(description="Key topics mentioned in the text")

class Entity(BaseModel):
    name: str
    type: str

class ExtractionResult(BaseModel):
    """Structured data extracted from text."""
    summary: str = Field(description="A brief summary of the input text")
    entities: List[Entity] = Field(description="List of entities found in the text")
    sentiment: SentimentAnalysis = Field(description="Sentiment analysis result")
