"""Local, stateless PDF-to-Colab application. No generated code is executed here."""
import asyncio
import re
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from generator import DEFAULT_MODEL, GenerationError, generate_tutorial, build_notebook, local_model_status
from paper import extract_paper

ROOT = Path(__file__).parent
MAX_BYTES = 12 * 1024 * 1024
app = FastAPI(title="Paper to Practice", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@app.middleware("http")
async def private_responses(request, call_next):
    # Reject cross-origin form submissions to this local service.
    origin = request.headers.get("origin")
    if request.method == "POST" and origin and origin != str(request.base_url).rstrip("/"):
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "Cross-origin requests are not allowed."}, status_code=403)
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    return response


@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


def valid_model(model: str):
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._:\-]{0,99}", model) or "cloud" in model.lower():
        raise HTTPException(400, "Enter a downloaded local Ollama model name, such as qwen3:4b-instruct.")


@app.get("/api/local-status")
async def local_status(model: str = DEFAULT_MODEL):
    valid_model(model)
    return await local_model_status(model)


@app.post("/api/generate")
async def generate(
    file: UploadFile = File(...),
    level: Literal["beginner", "intermediate", "advanced"] = Form("intermediate"),
    focus: str = Form("", max_length=1000),
    model: str = Form(DEFAULT_MODEL, max_length=100),
):
    try:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(400, "Please upload a .pdf file.")
        data = await file.read(MAX_BYTES + 1)
    finally:
        await file.close()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "The PDF exceeds 12 MB. Please compress it first.")
    valid_model(model)
    try:
        paper = await asyncio.to_thread(extract_paper, data)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None
    try:
        tutorial = await generate_tutorial(paper.text, level, focus, model)
        notebook = build_notebook(tutorial, file.filename, paper.pages, model, paper.notes)
    except GenerationError as exc:
        raise HTTPException(exc.status, str(exc)) from None
    safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "-", tutorial.title).strip("-")[:70] or "research-tutorial"
    return {"notebook": notebook, "filename": f"{safe_name}.ipynb", "title": tutorial.title,
            "summary": tutorial.summary, "pages": paper.pages, "source_notes": paper.notes,
            "validation": "Notebook format and Python syntax checked. Code has not been executed."}
