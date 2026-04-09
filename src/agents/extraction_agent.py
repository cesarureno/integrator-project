import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def extract_contract_changes(original: str, amended: str, context: str) -> dict:
    """
    Acts as a Legal Auditor to identify aditions, deletions, and modifications.
    Uses structural context to improve accuracy and returns a structured JSON result.
    """
    # 1. Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    
    client = OpenAI(api_key=api_key)

    # 2. Define the System and User Prompts
    system_prompt = (
        "You are a Legal Auditor. Your task is to identify and classify changes between an original and an amended contract. "
        "Classification categories: additions, deletions, modifications. "
        "You MUST return ONLY a valid JSON object. No explanations, no markdown, no text outside the JSON."
    )

    user_prompt = (
        "Compare the following contract versions using the provided structural context.\n\n"
        "### STRUCTURAL CONTEXT:\n"
        f"{context}\n\n"
        "### ORIGINAL CONTRACT:\n"
        f"{original}\n\n"
        "### AMENDED CONTRACT:\n"
        f"{amended}\n\n"
        "### INSTRUCTIONS:\n"
        "1. Identify real changes in terms, conditions, values, or clauses.\n"
        "2. In the 'sections_changed' field, use descriptive names (e.g., 'Pago', 'Plazo', 'Soporte') instead of section numbers.\n"
        "3. Return EXACTLY this JSON structure:\n"
        "{\n"
        "  \"sections_changed\": [\"string\"],\n"
        "  \"topics_touched\": [\"string\"],\n"
        "  \"summary_of_the_change\": \"string\"\n"
        "}"
    )

    try:
        # 3. Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )

        # 4. Extract and parse the JSON
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        
        # Basic validation of keys
        required_keys = ["sections_changed", "topics_touched", "summary_of_the_change"]
        if not all(key in data for key in required_keys):
            raise ValueError(f"API response missing required keys. Found: {data.keys()}")

        return data

    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error parsing JSON response from OpenAI: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error during extraction: {str(e)}")

if __name__ == "__main__":
    # Example usage
    pass
