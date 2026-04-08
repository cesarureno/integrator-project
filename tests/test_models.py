from src.models import ExtractionResult, SentimentAnalysis, Entity

def test_sentiment_analysis_validation():
    # Valid data
    data = {
        "sentiment": "positive",
        "score": 0.95,
        "keywords": ["fast", "reliable"]
    }
    sentiment = SentimentAnalysis(**data)
    assert sentiment.sentiment == "positive"
    assert sentiment.score == 0.95

def test_extraction_result_validation():
    data = {
        "summary": "Test summary",
        "entities": [{"name": "Google", "type": "Organization"}],
        "sentiment": {
            "sentiment": "neutral",
            "score": 0.5,
            "keywords": ["test"]
        }
    }
    result = ExtractionResult(**data)
    assert result.summary == "Test summary"
    assert len(result.entities) == 1
    assert result.entities[0].name == "Google"
