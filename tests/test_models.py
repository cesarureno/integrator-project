import pytest
from src.models import validate_output, ContractChangeOutput

def test_validate_output_success():
    valid_data = {
        "sections_changed": ["Pago", "Plazo"],
        "topics_touched": ["Amount", "Duration"],
        "summary_of_the_change": "Price increased and duration extended."
    }
    result = validate_output(valid_data)
    assert isinstance(result, ContractChangeOutput)
    assert result.sections_changed == ["Pago", "Plazo"]
    assert result.summary_of_the_change == "Price increased and duration extended."

def test_validate_output_missing_field():
    invalid_data = {
        "sections_changed": ["Pago"],
        # "topics_touched" is missing
        "summary_of_the_change": "Missing field test"
    }
    with pytest.raises(ValueError) as excinfo:
        validate_output(invalid_data)
    assert "topics_touched" in str(excinfo.value)
    assert "Field required" in str(excinfo.value)

def test_validate_output_wrong_type():
    invalid_data = {
        "sections_changed": "Not a list",  # Should be a list
        "topics_touched": ["Type"],
        "summary_of_the_change": "Wrong type test"
    }
    with pytest.raises(ValueError) as excinfo:
        validate_output(invalid_data)
    assert "sections_changed" in str(excinfo.value)
    assert "Input should be a valid list" in str(excinfo.value)
