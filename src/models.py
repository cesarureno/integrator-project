from pydantic import BaseModel, ValidationError
from typing import List

class SummaryByCategory(BaseModel):
    """
    Sub-model representing the breakdown of changes by category.
    """
    modifications: List[str]
    additions: List[str]
    deletions: List[str]

class ContractChangeOutput(BaseModel):
    """
    Pydantic model representing the structured output of contract changes.
    """
    sections_changed: List[str]
    topics_touched: List[str]
    summary_of_the_change: SummaryByCategory

def validate_output(data: dict) -> ContractChangeOutput:
    """
    Validates a dictionary against the ContractChangeOutput schema.
    
    Args:
        data (dict): The dictionary to validate.
        
    Returns:
        ContractChangeOutput: The validated Pydantic object.
        
    Raises:
        ValueError: If validation fails, with a clear error message.
    """
    try:
        # Use model_validate for Pydantic v2 compatibility
        validated_data = ContractChangeOutput.model_validate(data)
        return validated_data
    except ValidationError as e:
        # Provide a clear, readable error message
        error_details = e.errors()
        error_msg = f"Validation Error: {len(error_details)} issues found.\n"
        for error in error_details:
            loc = " -> ".join(map(str, error['loc']))
            msg = error['msg']
            error_msg += f"- {loc}: {msg}\n"
        raise ValueError(error_msg)
    except Exception as e:
        # Catch-all for unexpected issues during validation
        raise RuntimeError(f"An unexpected error occurred during validation: {str(e)}")

# Example usage (for internal module testing)
if __name__ == "__main__":
    test_data = {
        "sections_changed": ["Pago"],
        "topics_touched": ["Money"],
        "summary_of_the_change": "Changed price"
    }
    try:
        obj = validate_output(test_data)
        print(f"Validated successfully: {obj.sections_changed}")
    except ValueError as err:
        print(err)
