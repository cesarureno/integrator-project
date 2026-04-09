import os
import sys
from dotenv import load_dotenv

# Ensure the src directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.image_parser import parse_contract_image
from src.agents.contextualization_agent import contextualize_contracts
from src.agents.extraction_agent import extract_contract_changes
from src.models import validate_output

def main():
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found.")
        return

    # Rutas a la imagenes de pruebas
    image_original_path = "data/test_contracts/documento_1__original.jpg"
    image_amended_path = "data/test_contracts/documento_1__enmienda.jpg"

    try:
        original = parse_contract_image(image_original_path)
        amended = parse_contract_image(image_amended_path)

        context = contextualize_contracts(original, amended)

        result = extract_contract_changes(original, amended, context)

        validated = validate_output(result)

        print("\n--- JSON OUTPUT ---\n")
        print(validated.model_dump())
    except Exception as e:
        print(f"\nError during execution: {e}")

if __name__ == "__main__":
    main()
