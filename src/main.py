import os
import sys
import json
from dotenv import load_dotenv
from langfuse import Langfuse

# Ensure the src directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.image_parser import parse_contract_image
from src.agents.contextualization_agent import contextualize_contracts
from src.agents.extraction_agent import extract_contract_changes
from src.models import validate_output

def show_menu():
    """Shows an interactive menu to select the contract example."""
    print("\n" + "="*50)
    print("📁 SELECTOR DE EJEMPLOS DE CONTRATO")
    print("="*50)
    print("1. 💻 Contrato de Licencia de Software (Ejemplo 1)")
    print("2. 💼 Contrato de Servicios de Consultoría (Ejemplo 2)")
    print("3. ☁️  Contrato de Servicio SaaS (Ejemplo 3)")
    print("4. ❌ Salir")
    print("="*50)
    
    while True:
        try:
            opcion = input("\nSeleccione una opción (1-4): ")
            if opcion in ["1", "2", "3", "4"]:
                return opcion
            else:
                print("⚠️  Opción no válida. Por favor, intente de nuevo.")
        except KeyboardInterrupt:
            return "4"

def main():
    load_dotenv()

    # Verify API Keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY no encontrada.")
        return

    # Initialize Langfuse
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_BASE_URL")
    )

    opcion = show_menu()
    
    if opcion == "4":
        print("\n👋 ¡Hasta luego!\n")
        return

    # Map options to filenames and types
    examples = {
        "1": {
            "name": "Software License",
            "orig": "data/test_contracts/documento_1__original.jpg",
            "amd": "data/test_contracts/documento_1__enmienda.jpg",
            "emoji": "💻"
        },
        "2": {
            "name": "Consultancy Services",
            "orig": "data/test_contracts/documento_2__original.jpg",
            "amd": "data/test_contracts/documento_2__enmienda.jpg",
            "emoji": "💼"
        },
        "3": {
            "name": "SaaS Service",
            "orig": "data/test_contracts/documento_3__original.jpg",
            "amd": "data/test_contracts/documento_3__enmienda.jpg",
            "emoji": "☁️"
        }
    }

    selection = examples[opcion]
    image_original_path = selection["orig"]
    image_amended_path = selection["amd"]
    contract_type = selection["name"]

    print(f"\n🚀 Iniciando Pipeline: {selection['emoji']} {contract_type}...")
    print("--------------------------------------------------")

    # Start main trace (in v3, a root span is the trace)
    # Using a name that includes the contract type for better Langfuse filtering
    trace = langfuse.start_span(name=f"contract-analysis-{contract_type.lower().replace(' ', '-')}")

    try:
        # Stage 1: OCR Original
        print("📄 [1/5] Analizando contrato original (OCR)...", end="", flush=True)
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
                "contract_type": contract_type,
                "model": "gpt-4o",
                "usage": usage_orig
            }
        )
        span_orig.end()
        print(" ✅")

        # Stage 2: OCR Amended
        print("📄 [2/5] Analizando contrato enmendado (OCR)...", end="", flush=True)
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
                "contract_type": contract_type,
                "model": "gpt-4o",
                "usage": usage_amd
            }
        )
        span_amd.end()
        print(" ✅")

        # Stage 3: Contextualization
        print("🧠 [3/5] Generando mapa contextual legal...", end="", flush=True)
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
                "contract_type": contract_type,
                "model": "gpt-4o",
                "usage": usage_ctx
            }
        )
        span_ctx.end()
        print(" ✅")

        # Stage 4: Extraction
        print("🔍 [4/5] Extrayendo cambios y auditoría detallada...", end="", flush=True)
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
                "contract_type": contract_type,
                "sections_count": len(result.get("sections_changed", [])),
                "model": "gpt-4o",
                "usage": usage_ext
            }
        )
        span_ext.end()
        print(" ✅")

        # Stage 5: Validation
        print("🛡️ [5/5] Validando integridad de datos con Pydantic...", end="", flush=True)
        validated = validate_output(result)
        print(" ✅")

        print("\n" + "="*50)
        print(f"📊 RESULTADO DEL ANÁLISIS: {contract_type}")
        print("="*50)
        
        # Pretty print JSON for better readability
        print(json.dumps(validated.model_dump(), indent=4, ensure_ascii=False))
        
        # Calculate global usage
        total_prompt = (usage_orig["prompt_tokens"] + usage_amd["prompt_tokens"] + 
                        usage_ctx["prompt_tokens"] + usage_ext["prompt_tokens"])
        total_completion = (usage_orig["completion_tokens"] + usage_amd["completion_tokens"] + 
                            usage_ctx["completion_tokens"] + usage_ext["completion_tokens"])
        total_tokens = (usage_orig["total_tokens"] + usage_amd["total_tokens"] + 
                        usage_ctx["total_tokens"] + usage_ext["total_tokens"])

        # Update main trace with the final result and global usage
        trace.update(
            input={
                "original_path": image_original_path,
                "amended_path": image_amended_path,
                "contract_type": contract_type
            },
            output=validated.model_dump(),
            metadata={
                "total_usage": {
                    "prompt_tokens": total_prompt,
                    "completion_tokens": total_completion,
                    "total_tokens": total_tokens
                },
                "contract_type": contract_type,
                "version": "1.1.0"
            }
        )
        # End main trace
        trace.end()
        
        # Flush traces to Langfuse
        langfuse.flush()
        print("\n✨ Proceso completado con éxito. Datos enviados a Langfuse.")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        trace.update(status_message=str(e), level="ERROR")
        langfuse.flush()

if __name__ == "__main__":
    main()
