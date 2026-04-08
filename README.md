# LangChain + Pydantic + OpenAI Project Template

This is a base structure for building AI-powered applications using LangChain, Pydantic for data validation, and OpenAI.

## Prerequisites

- Python 3.9+
- OpenAI API Key

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and add your `OPENAI_API_KEY`.

## Project Structure

- `main.py`: Entry point for the application.
- `src/`:
  - `models.py`: Pydantic models for structured data.
  - `chain.py`: LangChain logic and configuration.
- `tests/`: Basic unit tests.

## Running the Example

```bash
python main.py
```

This will run a sample extraction task that takes a paragraph about Apple Inc. and transforms it into a structured JSON-like object validated by Pydantic.

## Testing

```bash
pytest
```
