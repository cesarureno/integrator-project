# Documentación Técnica: Pipeline de Extracción de Contratos

## 1. Descripción del Módulo
Este componente es el **punto de entrada multimodal** del sistema. Su función principal es convertir imágenes de contratos (formatos JPG, PNG, etc.) en texto plano altamente estructurado. A diferencia de un OCR tradicional, este módulo utiliza **Vision LLM (GPT-4o)** para realizar un "OCR semántico", interpretando no solo los caracteres sino también la jerarquía y el contexto de las cláusulas legales.

## 2. Decisiones Técnicas (Justificación)
*   **GPT-4o vs OCR Tradicional (Tesseract/Textract)**: Se eligió GPT-4o porque los contratos suelen tener layouts complejos, firmas superpuestas o sellos. Los OCRs tradicionales fallan en mantener la relación espacial. GPT-4o entiende la "forma" de un contrato y puede reconstruir secciones aunque la imagen tenga ruido.
*   **Base64 Encoding**: Se implementó la conversión a Base64 local para evitar exponer archivos en buckets públicos temporales, aumentando la privacidad de los documentos legales procesados.
*   **Manejo de Errores Desacoplado**: El uso de excepciones personalizadas (`FileNotFoundError`, `RuntimeError`) permite que el pipeline superior (donde estará la lógica de negocio) decida si reintentar o abortar el proceso sin colapsar la aplicación.

## 3. Conexión con el Pipeline General
El flujo de datos está diseñado de forma modular:
1.  **Ingesta**: `src/image_parser.py` recibe la ruta del archivo y devuelve un `string` gigante con el texto crudo.
2.  **Transformación**: Ese texto se pasa a `src/chain.py`.
3.  **Validación**: LangChain y Pydantic (`src/models.py`) toman ese texto crudo y lo "encasillan" en objetos de Python validados, asegurando que el sistema final siempre reciba datos con el formato correcto (ej: fecha de contrato, partes involucradas, monto).

## 4. Análisis de Errores y Riesgos
*   **Límites de Tokens**: Imágenes con texto extremadamente denso podrían exceder la ventana de salida.
*   **Costos**: El uso de modelos multimodales es más caro que el OCR estándar; por ello, este módulo debe usarse solo para la extracción inicial.
*   **Hallucinaciones y Bloqueos**: GPT-4o puede rechazar documentos legales si cree que se le pide "asesoría". Para mitigar esto, usamos un prompt de **transcripción neutral (estilo OCR)** que desactiva funciones analíticas y se enfoca solo en la extracción de texto crudo. La validación posterior con Pydantic actúa como un filtro de seguridad adicional.

## 6. Agente de Contextualización Estructural

Este agente (`src/agents/contextualization_agent.py`) actúa como un **Analista Legal Senior** cuyo objetivo no es extraer datos específicos, sino entender la "geografía" de los documentos.

### 1. ¿Qué hace este agente?
Analiza simultáneamente el contrato original y su enmienda para crear un mapa de correspondencias estructurales. Identifica que la "Cláusula 3" del documento A corresponde a la "Sección 3" del documento B, describiendo el propósito legal de cada una (ej. Pago, Confidencialidad).

### 2. ¿Por qué está separado del Agente de Extracción?
*   **Principio de Responsabilidad Única (SRP)**: La extracción de datos (Pydantic) es una tarea de precisión sobre campos específicos. La contextualización es una tarea de comprensión global y estructural. Separarlos reduce la carga cognitiva del modelo en cada paso, mejorando la precisión.
*   **Escalabilidad**: Podemos cambiar la estructura de extracción sin afectar cómo mapeamos los documentos.

### 3. Conexión con el Pipeline
El agente recibe los textos crudos ya procesados por el `image_parser`. Su salida está **optimizada para el consumo de otros agentes**, utilizando un formato compacto que reduce el ruido de tokens y se enfoca en identificadores de referencia (`Orig Ref -> Amd Ref`). Este mapa sirve como el "plano" estructural para los siguientes pasos del pipeline.


### 4. Defensa Técnica
"El Agente de Contextualización elimina la ambigüedad estructural antes de cualquier intento de comparación. Al mapear las secciones primero, garantizamos que las futuras comparaciones de 'deltas' se realicen 'manzanas con manzanas', independientemente de si la numeración o el formato cambiaron en la enmienda."

## 7. Agente de Extracción (Auditor Legal)

Este agente (`src/agents/extraction_agent.py`) es el motor lógico final que identifica y clasifica los cambios de contenido entre los documentos.

### 1. ¿Qué hace este agente?
Actúa como un Auditor Legal que busca adiciones, eliminaciones y modificaciones específicas en las cláusulas. Su salida es un **JSON determinista** que contiene las secciones afectadas, los temas tocados (topics) y un resumen ejecutivo del cambio.

### 2. ¿Por qué depende del Agente de Contextualización?
Depender del mapa estructural previo permite que el Agente de Extracción:
*   **Reduzca el "Search Space"**: Sabe exactamente qué secciones comparar.
*   **Evite falsos positivos**: No interpreta un cambio de numeración como una eliminación de cláusula.
*   **Aumente la densidad de información**: Al no gastar tokens en entender la estructura, puede enfocarse al 100% en la semántica de los cambios.

### 3. Validación con Pydantic (Futuro)
Aunque el agente devuelve un JSON crudo, este se valida inmediatamente después del retorno mediante un esquema de Pydantic. Esto garantiza que cualquier anomalía en la respuesta de la IA (ej. campo faltante o formato incorrecto) sea detectada antes de impactar al usuario.

## 8. Validación de Datos (Pydantic)

Se ha implementado una capa de validación robusta (`src/models.py`) utilizando Pydantic para asegurar que la salida de los modelos de lenguaje sea determinista y consistente.

### 1. ¿Por qué es importante Pydantic en este sistema?
Los Modelos de Lenguaje (LLMs) son probabilísticos y, aunque se les pida JSON, pueden fallar en la estructura o en los tipos de datos. Pydantic actúa como un **contrato de interfaz** fuerte. Si el LLM comete un error (ej. olvida una coma o envía un número en lugar de una lista), Pydantic lo detecta inmediatamente, evitando que datos corruptos entren en la lógica de negocio.

### 2. ¿Qué problema resuelve en producción?
*   **Integridad de Datos**: Garantiza que `sections_changed` siempre sea una lista, permitiendo que el backend o frontend itere sobre ella sin riesgo de errores tipo `TypeError`.
*   **Fail-Fast**: Ante una respuesta malformada, el sistema lanza una excepción controlada (`ValueError`) en lugar de fallar silenciosamente o causar comportamientos erráticos más adelante en el pipeline.
*   **Documentación Viva**: El modelo de Pydantic sirve como la "única fuente de verdad" sobre el esquema de datos del proyecto.

### 3. Defensa Técnica
"Nuestra arquitectura no confía ciegamente en la IA. Utilizamos Pydantic para validar cada respuesta contra un esquema riguroso. Esto transforma una salida generativa en un objeto de datos tipado y confiable, cumpliendo con los estándares de robustez requeridos para software empresarial y auditoría legal."

## 9. Observabilidad y Trazabilidad (Langfuse)

Se ha integrado **Langfuse** para proporcionar una visión clara y detallada de lo que sucede "bajo el capó" en cada ejecución del pipeline.

### 1. ¿Cómo funciona la trazabilidad?
Cada ejecución genera un `trace` único llamado `contract-analysis`. Dentro de este, se crean `spans` para cada etapa lógica (OCR, Contextualización, Extracción). Cada span registra:
*   **Inputs**: Rutas de archivos o textos de entrada.
*   **Outputs**: Resultados parciales, longitudes de texto y estructuras JSON.
*   **Metadatos**: Información técnica que permite filtrar y agrupar ejecuciones.

### 2. Ventajas para Debugging y Auditoría
- **Aislamiento de Errores**: Permite identificar si un fallo ocurrió en la fase de visión (OCR) o en la lógica de algún agente (LLM).
- **Optimización de Prompts**: Al ver el input exacto que se envió al modelo y su respuesta, podemos iterar sobre los prompts con datos reales.
- **Auditoría de Costos (Token Tracking)**: El sistema registra el uso de tokens (prompt, completion y total) en cada etapa. Esto permite calcular el costo exacto de procesamiento por contrato y optimizar el consumo.
- **Métricas de Performance**: Registro automático de latencia y metadatos detallados (longitud de texto, preview de contenido) para monitorear la eficiencia y salud del pipeline.

### 3. Defensa Técnica
"La inteligencia artificial en producción suele ser una 'caja negra'. Nuestra integración con Langfuse elimina este riesgo, proporcionando **observabilidad total**. Esto no solo facilita el mantenimiento preventivo, sino que permite implementar ciclos de mejora continua basados en datos reales de ejecución, garantizando que el sistema sea auditable y transparente."
