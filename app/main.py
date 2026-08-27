import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, field_validator

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

app = FastAPI(title="AI Meeting Notes Summarizer")


class SummarizeRequest(BaseModel):
    notes: str

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("notes must be a non-empty string (max 8000 characters)")
        if len(value) > 8000:
            raise ValueError("notes must be a non-empty string (max 8000 characters)")
        return value


class ActionItem(BaseModel):
    task: str
    owner: str | None


class SummarizeResponse(BaseModel):
    summary: list[str]
    action_items: list[ActionItem]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(body: SummarizeRequest) -> SummarizeResponse:
    if client is None:
        raise HTTPException(status_code=500, detail="Failed to summarize notes")

    prompt = (
        "Summarize the following meeting notes as concise bullet points "
        "and extract action items with owners when mentioned.\n\n"
        f"{body.notes}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=SummarizeResponse,
            ),
        )
        parsed = response.parsed
        if parsed is None:
            raise ValueError("empty model response")
        return parsed
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to summarize notes")
