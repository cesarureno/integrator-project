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
        "Eres un Auditor Legal de alta precisión. Tu responsabilidad es identificar, aislar y describir minuciosamente cada cambio introducido en un contrato mediante su enmienda. "
        "Debes actuar con un rigor extremo, comparando cláusula por cláusula para detectar diferencias sutiles pero legalmente significativas. "
        "DEBES clasificar los hallazgos en tres categorías: Adiciones, Eliminaciones y Modificaciones. "
        "Tu salida DEBE consistir únicamente en un objeto JSON válido, sin preámbulos, markdown ni texto adicional. "
        "TODA la redacción dentro del JSON debe estar en ESPAÑOL profesional y técnico."
    )

    user_prompt = (
        "Realiza una auditoría exhaustiva de cambios comparando el contrato original con su enmienda, utilizando el mapa estructural proporcionado como guía.\n\n"
        "### CONTEXTO ESTRUCTURAL (GUÍA DE MAPEADO):\n"
        f"{context}\n\n"
        "### CONTRATO ORIGINAL (TEXTO COMPLETO):\n"
        f"{original}\n\n"
        "### CONTRATO ENMENDADO (TEXTO COMPLETO):\n"
        f"{amended}\n\n"
        "### INSTRUCCIONES DE AUDITORÍA:\n"
        "1. **Comparación Cláusula a Cláusula**: Recorre cada entrada del contexto estructural y busca diferencias exactas en el texto.\n"
        "2. **Detección de Modificaciones**: Identifica cambios en valores numéricos, fechas, plazos, alcances de licencias o términos de pago dentro de cláusulas existentes.\n"
        "3. **Identificación de Adiciones**: Localiza cláusulas, párrafos o secciones que aparecen en la enmienda pero no tienen correspondencia en el original.\n"
        "4. **Identificación de Eliminaciones**: Localiza contenido presente en el original que ha sido omitido o expresamente eliminado en la enmienda.\n"
        "5. **Sin Restricciones de Brevedad**: No seas conciso. Describe detalladamente el impacto de cada cambio. Prioriza la precisión legal sobre la brevedad.\n"
        "6. **Formato de Salida**: Genera un JSON con esta estructura exacta (IMPORTANTE: 'summary_of_the_change' debe ser un OBJETO):\n"
        "{\n"
        "  \"sections_changed\": [\"Nombre descriptivo de la sección/cláusula afectada\"],\n"
        "  \"topics_touched\": [\"Temas legales específicos (ej: Propiedad Intelectual, Responsabilidad Civil)\"],\n"
        "  \"summary_of_the_change\": {\n"
        "    \"modificaciones\": \"Reporte detallado de términos modificados...\",\n"
        "    \"adiciones\": \"Reporte detallado de nuevas cláusulas o párrafos...\",\n"
        "    \"eliminaciones\": \"Reporte detallado de contenido removido...\"\n"
        "  }\n"
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

        # 5. Get usage metadata
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        return data, usage

    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error parsing JSON response from OpenAI: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error during extraction: {str(e)}")

if __name__ == "__main__":
    # Example usage
    pass
