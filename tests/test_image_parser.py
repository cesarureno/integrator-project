import pytest
from unittest.mock import MagicMock, patch
from src.image_parser import parse_contract_image, encode_image

def test_encode_image_file_not_found():
    with pytest.raises(FileNotFoundError):
        encode_image("non_existent_file.jpg")

@patch("os.path.exists")
def test_parse_contract_image_file_not_found(mock_exists):
    mock_exists.return_value = False
    with pytest.raises(FileNotFoundError):
        parse_contract_image("missing.jpg")

@patch("src.image_parser.OpenAI")
@patch("src.image_parser.encode_image")
@patch("os.path.exists")
@patch("os.getenv")
def test_parse_contract_image_success(mock_getenv, mock_exists, mock_encode, mock_openai_class):
    # Setup mocks
    mock_getenv.return_value = "fake_api_key"
    mock_exists.return_value = True
    mock_encode.return_value = "base64_string"
    
    # Mock OpenAI client response
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="Extracted contract text"))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    # Execute
    result = parse_contract_image("dummy_path.jpg")
    
    # Assert
    assert result == "Extracted contract text"
    mock_client.chat.completions.create.assert_called_once()
    args, kwargs = mock_client.chat.completions.create.call_args
    assert kwargs["model"] == "gpt-4o"
    assert "image_url" in str(kwargs["messages"])

@patch("src.image_parser.OpenAI")
@patch("src.image_parser.encode_image")
@patch("os.path.exists")
@patch("os.getenv")
def test_parse_contract_image_api_error(mock_getenv, mock_exists, mock_encode, mock_openai_class):
    # Setup mocks
    mock_getenv.return_value = "fake_api_key"
    mock_exists.return_value = True
    mock_encode.return_value = "base64_string"
    
    # Mock OpenAI client to raise an exception
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API Key Invalid")
    
    # Execute and Assert
    with pytest.raises(RuntimeError) as excinfo:
        parse_contract_image("dummy_path.jpg")
    assert "Error calling OpenAI API" in str(excinfo.value)
