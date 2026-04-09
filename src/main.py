import os
import sys
from dotenv import load_dotenv
from langfuse import Langfuse

# Ensure the src directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.image_parser import parse_contract_image
from src.agents.contextualization_agent import contextualize_contracts
from src.agents.extraction_agent import extract_contract_changes
from src.models import validate_output

def main():
    load_dotenv()

    # Verify API Keys
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found.")
        return

    # Initialize Langfuse
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_BASE_URL")
    )

    # Start main trace (in v3, a root span is the trace)
    trace = langfuse.start_span(name="contract-analysis")

    # Image paths
    image_original_path = "data/test_contracts/documento_1__original.jpg"
    image_amended_path = "data/test_contracts/documento_1__enmienda.jpg"

    try:
        # Stage 1: OCR Original
        span_orig = trace.start_span(
            name="parse_original_contract", 
            input={
                "path": image_original_path
            }
        )
        original = parse_contract_image(image_original_path)
        span_orig.update(output={"text_length": len(original), "preview": original[:100]})
        span_orig.end()

        # Stage 2: OCR Amended
        span_amd = trace.start_span(name="parse_amendment_contract", input={"path": image_amended_path})
        amended = parse_contract_image(image_amended_path)
        span_amd.update(output={"text_length": len(amended), "preview": amended[:100]})
        span_amd.end()

        # Stage 3: Contextualization
        span_ctx = trace.start_span(
            name="contextualization_agent", 
            input={"original_len": len(original), "amended_len": len(amended)}
        )
        context = contextualize_contracts(original, amended)
        span_ctx.update(output={"context": context})
        span_ctx.end()

        # Stage 4: Extraction
        span_ext = trace.start_span(name="extraction_agent", input={"context_len": len(context)})
        result = extract_contract_changes(original, amended, context)
        span_ext.update(output=result)
        span_ext.end()

        # Stage 5: Validation
        validated = validate_output(result)

        print("\n--- JSON OUTPUT ---\n")
        print(validated.model_dump())
        
        # Update main trace with the final result
        trace.update(
            name="contract-analysis",
            input={
                "original_path": image_original_path,
                "amended_path": image_amended_path
            },
            output=validated.model_dump()
        )
        # End main trace
        trace.end()
        
        # Flush traces to Langfuse
        langfuse.flush()

    except Exception as e:
        print(f"\nError during execution: {e}")
        trace.update(status_message=str(e), level="ERROR")
        langfuse.flush()

if __name__ == "__main__":
    main()
