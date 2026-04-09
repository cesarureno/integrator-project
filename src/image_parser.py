import os
import base64
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

def encode_image(image_path: str) -> str:
    """Encodes an image to a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def parse_contract_image(image_path: str) -> str:
    """
    Parses a contract image using OpenAI's GPT-4o model.
    Extracts all text while maintaining structure and sections.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"The file {image_path} does not exist.")

    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    
    client = OpenAI(api_key=api_key)

    try:
        # Encode image to base64
        base64_image = encode_image(image_path)

        # Prompt definition
        prompt = (
            "You are an OCR-like system specialized in extracting text from documents.\n\n"
            "Extract ALL visible text from this contract image.\n\n"
            "Rules:\n"
            "- Do NOT summarize\n"
            "- Do NOT analyze\n"
            "- Do NOT interpret\n"
            "- Just transcribe exactly what you see\n"
            "- Preserve structure, sections, numbering and formatting as much as possible\n\n"
            "Return only the extracted text."
        )

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=4096,
            temperature=0.0,
        )

        # Extract and return the content
        return response.choices[0].message.content.strip()

    except Exception as e:
        # General error handling for API issues
        raise RuntimeError(f"Error calling OpenAI API: {str(e)}")

if __name__ == "__main__":
    # Example usage for testing purposes
    # test_image = "path/to/your/contract.jpg"
    # try:
    #     text = parse_contract_image(test_image)
    #     print(text)
    # except Exception as err:
    #     print(f"Error: {err}")
    pass
