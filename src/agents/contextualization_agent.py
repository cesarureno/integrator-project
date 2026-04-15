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
        "Eres un Analista Legal Senior. Tu tarea es extraer un mapa estructural de dos contratos. "
        "La salida debe estar optimizada para el procesamiento posterior por IA. "
        "Toda la respuesta debe estar en ESPAÑOL."
    )

    user_prompt = (
        "Analiza estos documentos de forma independiente y construye un mapa estructural.\n\n"
        f"ORIGINAL:\n{original}\n\n"
        f"AMENDED:\n{amended}\n\n"
        "INSTRUCCIONES ESTRICTAS:\n"
        "1. Lista las secciones de cada documento: [Ref] [Nombre]: [Propósito]\n"
        "2. El propósito debe tener menos de 40 palabras y NO contener valores/fechas/montos específicos.\n"
        "3. Mapea las secciones: [Ref Original] -> [Ref Enmienda]\n"
        "4. No incluyas texto conversacional ni encabezados largos.\n"
        "5. TODO el contenido debe estar en ESPAÑOL."
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

        # 4. Extract and return the result and usage
        content = response.choices[0].message.content.strip()
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
        return content, usage

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
