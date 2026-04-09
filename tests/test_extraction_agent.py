import pytest
import json
from unittest.mock import MagicMock, patch
from src.agents.extraction_agent import extract_contract_changes

@patch("src.agents.extraction_agent.OpenAI")
@patch("os.getenv")
def test_extract_contract_changes_success(mock_getenv, mock_openai_class):
    # Setup mocks
    mock_getenv.return_value = "fake_api_key"
    
    # Mock OpenAI client response
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_json_response = {
        "sections_changed": ["Clause 2", "Clause 5"],
        "topics_touched": ["Duration", "Notice Period"],
        "summary_of_the_change": "Increased duration to 24 months and notice period to 60 days."
    }
    
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps(mock_json_response)))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    # Execute
    result = extract_contract_changes("Original Text", "Amended Text", "Structural Context")
    
    # Assert
    assert result == mock_json_response
    mock_client.chat.completions.create.assert_called_once()
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["response_format"] == {"type": "json_object"}

@patch("src.agents.extraction_agent.OpenAI")
@patch("os.getenv")
def test_extract_contract_changes_invalid_json(mock_getenv, mock_openai_class):
    # Setup mocks
    mock_getenv.return_value = "fake_api_key"
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Invalid JSON Content"))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    # Execute and Assert
    with pytest.raises(RuntimeError) as excinfo:
        extract_contract_changes("Original", "Amended", "Context")
    assert "Error parsing JSON response" in str(excinfo.value)
