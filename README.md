# Pipeline de Análisis de Contratos con IA

Este proyecto implementa un pipeline automatizado para el procesamiento y auditoría de contratos legales utilizando visión artificial y agentes inteligentes.

## 🛠️ Tecnologías Utilizadas

- **Python 3.9+**: Lenguaje base del proyecto.
- **OpenAI API (GPT-4o)**: Utilizado para visión multimodal y análisis semántico.
- **Pydantic**: Para la definición de modelos de datos y validación de estructuras.
- **python-dotenv**: Gestión de variables de entorno para seguridad.
- **Pytest/Unittest**: Framework de pruebas unitarias con uso de Mocks.

## 📋 Implementación y Funcionalidades

El sistema sigue un flujo modular dividido en tres etapas principales:

1. **OCR Semántico**: Conversión de imágenes de contratos a texto plano manteniendo la estructura original (secciones, numeración y párrafos).
2. **Mapeo Estructural**: Agente especializado que analiza y correlaciona las secciones entre un contrato original y su enmienda, creando un mapa de correspondencias independiente del contenido.
3. **Auditoría Legal**: Agente de extracción que identifica adiciones, eliminaciones y modificaciones críticas, generando un output estructurado en formato JSON.

## ⚖️ Buenas Prácticas

- **Principio de Responsabilidad Única (SRP)**: Cada agente y módulo tiene una única función clara (Visión, Estructura, Extracción).
- **Inyección de Dependencias**: Uso de cliente OpenAI configurado mediante variables de entorno.
- **Manejo de Excepciones**: Implementación de bloques try-except para gestionar fallos de API y errores de archivo (FileNotFound).
- **Salida Determinista**: Uso de `response_format={"type": "json_object"}` para garantizar JSONs válidos.
- **Conventional Commits**: El proyecto sigue el estándar de mensajes de commit informativos y estructurados.

## 🧪 Pruebas Unitarias

Se ha implementado una suite de pruebas para garantizar la confiabilidad del código:
- Pruebas para el motor de visión (`tests/test_image_parser.py`).
- Pruebas para agentes con interceptación de llamadas API mediante `unittest.mock`.

Para ejecutar los tests:
```bash
pytest
```

## 🚀 Instalación y Uso

1. **Configurar entorno**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Configurar API Key**:
   - Copiar `.env.example` a `.env` y añadir tu `OPENAI_API_KEY`.
3. **Ejecutar Pipeline**:
   ```bash
   python -m src.main
   ```
