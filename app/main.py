import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, field_validator

load_dotenv()

# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Create Gemini client
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# FastAPI app
app = FastAPI(title="AI Meeting Notes Summarizer")


# --------------------------------------------------
# Request Model
# --------------------------------------------------

class SummarizeRequest(BaseModel):
    notes: str

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Notes must be a non-empty string")

        if len(value) > 30000:
            raise ValueError(
                "Notes must not exceed 30,000 characters"
            )

        return value


# --------------------------------------------------
# Action Item Model
# --------------------------------------------------

class ActionItem(BaseModel):
    task: str
    owner: str | None = None


# --------------------------------------------------
# Response Model
# --------------------------------------------------

class SummarizeResponse(BaseModel):
    summary: list[str]
    action_items: list[ActionItem]


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# --------------------------------------------------
# Summarize Meeting Notes
# --------------------------------------------------

@app.post("/summarize", response_model=SummarizeResponse)
def summarize(body: SummarizeRequest) -> SummarizeResponse:

    # Check API key
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured"
        )

    # Prompt
    prompt = f"""
You are an AI meeting notes summarizer.

Analyze the following meeting notes and return:

1. A concise summary as bullet points.
2. All important action items.
3. The owner/person responsible for each action item if mentioned.
4. If an action item has no owner mentioned, set owner to null.
5. Do not invent information that is not present in the meeting notes.
6. Keep the summary concise but include important decisions, deadlines,
   problems, and responsibilities.

Meeting Notes:
----------------
{body.notes}
----------------
"""

    try:
        # Send request to Gemini
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
            raise ValueError("Gemini returned an empty response")

        return parsed

    except Exception as e:
        print("Gemini Error:", e)

        raise HTTPException(
            status_code=500,
            detail=f"Failed to summarize notes: {str(e)}"
        )
