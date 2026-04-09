import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def contextualize_contracts(original: str, amended: str) -> str:
    """
    Acts as a Senior Legal Analyst to map the structure of two contracts.
    Identifies sections and their purposes without comparing changes.
    """
    # 1. Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    
    client = OpenAI(api_key=api_key)

    # 2. Define the System and User Prompts
    system_prompt = (
        "You are a Senior Legal Analyst. Your task is to extract a structural map from two contracts. "
        "Output MUST be extremely compact and concise, optimized for follow-on AI processing."
    )

    user_prompt = (
        "Analyze these documents independently and build a structural map.\n\n"
        f"ORIGINAL:\n{original}\n\n"
        f"AMENDED:\n{amended}\n\n"
        "STRICT INSTRUCTIONS:\n"
        "1. List sections for each document: [Ref] [Name]: [Purpose]\n"
        "2. Purpose must be < 15 words and contain NO specific values/dates/amounts.\n"
        "3. Map sections: [Orig Ref] -> [Amd Ref]\n"
        "4. No conversational text or long headings.\n"
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
        )

        # 4. Extract and return the result
        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"Error during contextualization: {str(e)}")

if __name__ == "__main__":
    # Example for testing
    # original_text = "..."
    # amended_text = "..."
    # try:
    #     map_result = contextualize_contracts(original_text, amended_text)
    #     print(map_result)
    # except Exception as err:
    #     print(f"Error: {err}")
    pass
