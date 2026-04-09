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
        span_orig = trace.start_observation(
            name="parse_original_contract", 
            as_type="generation",
            input={"path": image_original_path}
        )
        original, usage_orig = parse_contract_image(image_original_path)
        span_orig.update(
            model="gpt-4o",
            usage_details={
                "input": usage_orig["prompt_tokens"],
                "output": usage_orig["completion_tokens"],
                "total": usage_orig["total_tokens"]
            },
            output={"text_length": len(original), "preview": original},
            metadata={
                "file_path": image_original_path, 
                "stage": "OCR_Original",
                "model": "gpt-4o",
                "usage": usage_orig
            }
        )
        span_orig.end()

        # Stage 2: OCR Amended
        span_amd = trace.start_observation(
            name="parse_amendment_contract", 
            as_type="generation",
            input={"path": image_amended_path}
        )
        amended, usage_amd = parse_contract_image(image_amended_path)
        span_amd.update(
            model="gpt-4o",
            usage_details={
                "input": usage_amd["prompt_tokens"],
                "output": usage_amd["completion_tokens"],
                "total": usage_amd["total_tokens"]
            },
            output={"text_length": len(amended), "preview": amended},
            metadata={
                "file_path": image_amended_path, 
                "stage": "OCR_Amended",
                "model": "gpt-4o",
                "usage": usage_amd
            }
        )
        span_amd.end()

        # Stage 3: Contextualization
        span_ctx = trace.start_observation(
            name="contextualization_agent", 
            as_type="generation",
            input={"original_len": len(original), "amended_len": len(amended)}
        )
        context, usage_ctx = contextualize_contracts(original, amended)
        span_ctx.update(
            model="gpt-4o",
            usage_details={
                "input": usage_ctx["prompt_tokens"],
                "output": usage_ctx["completion_tokens"],
                "total": usage_ctx["total_tokens"]
            },
            output={"context_preview": context},
            metadata={
                "stage": "Contextualization",
                "model": "gpt-4o",
                "usage": usage_ctx
            }
        )
        span_ctx.end()

        # Stage 4: Extraction
        span_ext = trace.start_observation(
            name="extraction_agent", 
            as_type="generation",
            input={"context_len": len(context)}
        )
        result, usage_ext = extract_contract_changes(original, amended, context)
        span_ext.update(
            model="gpt-4o",
            usage_details={
                "input": usage_ext["prompt_tokens"],
                "output": usage_ext["completion_tokens"],
                "total": usage_ext["total_tokens"]
            },
            output=result,
            metadata={
                "stage": "Extraction", 
                "sections_count": len(result.get("sections_changed", [])),
                "model": "gpt-4o",
                "usage": usage_ext
            }
        )
        span_ext.end()

        # Stage 5: Validation
        validated = validate_output(result)

        print("\n--- JSON OUTPUT ---\n")
        print(validated.model_dump())
        
        # Calculate global usage
        total_prompt = (usage_orig["prompt_tokens"] + usage_amd["prompt_tokens"] + 
                        usage_ctx["prompt_tokens"] + usage_ext["prompt_tokens"])
        total_completion = (usage_orig["completion_tokens"] + usage_amd["completion_tokens"] + 
                            usage_ctx["completion_tokens"] + usage_ext["completion_tokens"])
        total_tokens = (usage_orig["total_tokens"] + usage_amd["total_tokens"] + 
                        usage_ctx["total_tokens"] + usage_ext["total_tokens"])

        # Update main trace with the final result and global usage
        trace.update(
            name="contract-analysis",
            input={
                "original_path": image_original_path,
                "amended_path": image_amended_path
            },
            output=validated.model_dump(),
            metadata={
                "total_usage": {
                    "prompt_tokens": total_prompt,
                    "completion_tokens": total_completion,
                    "total_tokens": total_tokens
                },
                "version": "1.0.0"
            }
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
