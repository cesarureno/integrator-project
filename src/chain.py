import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from .models import ExtractionResult

# Load environment variables
load_dotenv()

def get_extraction_chain():
    """
    Initializes and returns a LangChain chain for structured data extraction.
    """
    # 1. Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini", # Or your preferred model
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # 2. Setup the Output Parser
    parser = PydanticOutputParser(pydantic_object=ExtractionResult)

    # 3. Define the Prompt Template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert data extractor. Extract the requested information from the text provided. \n{format_instructions}"),
        ("user", "{text}")
    ]).partial(format_instructions=parser.get_format_instructions())

    # 4. Construct the Chain
    chain = prompt | llm | parser

    return chain
