import os
import sys
from dotenv import load_dotenv

# Ensure the src directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.chain import get_extraction_chain

def main():
    # Load environment variables
    load_dotenv()

    # Check for API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment.")
        print("Please copy .env.example to .env and add your OpenAI API key.")
        return

    # Initialize the chain
    print("--- Initializing LangChain ---")
    chain = get_extraction_chain()

    # Sample text for extraction
    sample_text = """
    Apple Inc. is an American multinational technology company headquartered in Cupertino, California. 
    It was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976. 
    The company is known for its iPhone, iPad, and Mac computers. 
    Users generally love the sleek design and ecosystem integration of their products.
    """

    print(f"--- Processing Input Text ---\n{sample_text.strip()}")
    
    try:
        # Execute the chain
        result = chain.invoke({"text": sample_text})
        
        # Display the validated Pydantic object
        print("\n--- Extracted Data (Pydantic Model) ---")
        print(f"Summary: {result.summary}")
        print("\nEntities:")
        for entity in result.entities:
            print(f"- {entity.name} ({entity.type})")
        
        print(f"\nSentiment: {result.sentiment.sentiment} (Score: {result.sentiment.score})")
        print(f"Keywords: {', '.join(result.sentiment.keywords)}")

    except Exception as e:
        print(f"\nError during execution: {e}")

if __name__ == "__main__":
    main()
