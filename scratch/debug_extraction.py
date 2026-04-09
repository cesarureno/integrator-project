import os
import sys
from dotenv import load_dotenv

# Ensure the src directory is in the path
sys.path.append(os.path.join(os.getcwd()))

from src.image_parser import parse_contract_image
from src.agents.contextualization_agent import contextualize_contracts
from src.agents.extraction_agent import extract_contract_changes

def debug_run():
    load_dotenv()
    
    image_original_path = "data/test_contracts/documento_1__original.jpg"
    image_amended_path = "data/test_contracts/documento_1__enmienda.jpg"

    print("Stage 1: Parsing Original...")
    original, _ = parse_contract_image(image_original_path)
    
    print("Stage 2: Parsing Amended...")
    amended, _ = parse_contract_image(image_amended_path)
    
    print("Stage 3: Contextualizing...")
    context, _ = contextualize_contracts(original, amended)
    
    print("Stage 4: Extracting...")
    result, _ = extract_contract_changes(original, amended, context)
    
    print("\n--- RAW RESULT FROM EXTRACTION AGENT ---")
    import pprint
    pprint.pprint(result)
    
    print("\nType of summary_of_the_change:", type(result.get("summary_of_the_change")))

if __name__ == "__main__":
    debug_run()
