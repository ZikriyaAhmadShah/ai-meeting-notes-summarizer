# Specification Document: AI Meeting Notes Summarizer

## Problem Statement
Professionals spend excessive time manually reviewing length meeting transcripts to extract key takeaways, decisions, and action items. The AI Meeting Notes Summarizer provides an automated solution that digests raw meeting text and generates structured summaries instantly.

## MVP Scope
1. **Transcript Summarization Route:** FastAPI endpoint (`POST /summarize`) accepting raw meeting text and returning a structured JSON payload via the Google GenAI SDK.
2. **Interactive Streamlit Dashboard:** User-friendly UI allowing text entry, standard model trigger execution, and formatted output display.
3. **Graceful Error Handling:** Input validation using Pydantic models with defensive error feedback on the Streamlit UI for empty submissions or upstream API failures.

## Tech Stack
- **Backend Framework:** FastAPI (Uvicorn)
- **Frontend Framework:** Streamlit
- **LLM SDK:** `google-genai` (Google Gemini API)
- **Configuration & Utilities:** `python-dotenv`, `pydantic`, `requests`

## Environment Setup
File: `.env.example`
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000