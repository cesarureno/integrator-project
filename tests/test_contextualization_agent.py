import pytest
from unittest.mock import MagicMock, patch
from src.agents.contextualization_agent import contextualize_contracts

@patch("src.agents.contextualization_agent.OpenAI")
@patch("os.getenv")
def test_contextualize_contracts_success(mock_getenv, mock_openai_class):
    # Setup mocks
    mock_getenv.return_value = "fake_api_key"
    
    # Mock OpenAI client response
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Structural Map Result"))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    # Execute
    result = contextualize_contracts("Original Text", "Amended Text")
    
    # Assert
    assert result == "Structural Map Result"
    mock_client.chat.completions.create.assert_called_once()
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4o"
    assert "Compare the structure" in str(kwargs["messages"])

@patch("src.agents.contextualization_agent.OpenAI")
@patch("os.getenv")
def test_contextualize_contracts_api_error(mock_getenv, mock_openai_class):
    # Setup mocks
    mock_getenv.return_value = "fake_api_key"
    
    # Mock OpenAI client to raise an exception
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    
    # Execute and Assert
    with pytest.raises(RuntimeError) as excinfo:
        contextualize_contracts("Original", "Amended")
    assert "Error during contextualization" in str(excinfo.value)
