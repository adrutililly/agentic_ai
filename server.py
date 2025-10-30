# server.py
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agentic_processing import run_task  # ✅ Using agentic version!

# --- FastAPI app ---
app = FastAPI(title="Agentic AI (LLM Gateway)", version="1.0.0")

# CORS (tweak for your UI domains)
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Schemas ---
class PromptRequest(BaseModel):
    prompt: str = Field(..., description="Natural-language instruction")
    model: Optional[str] = Field(None, description="Override LLM model (e.g., gpt-4o-mini)")
    system: Optional[str] = Field(None, description="Override system instructions for this call")

class PromptResponse(BaseModel):
    output: str

# --- Routes ---
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/prompt", response_model=PromptResponse)
def post_prompt(req: PromptRequest):
    try:
        output = run_task(
            user_prompt=req.prompt,
            system_instructions=req.system,
            model=req.model,
        )
        return PromptResponse(output=output)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))