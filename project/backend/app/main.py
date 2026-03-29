import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

from app.kb_loader import load_knowledge_base
from app.models import ChatRequest, ChatResponse
from app.prompts import SYSTEM_PROMPT, build_user_prompt
from app.rag import SimpleRAG

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
KB_PATH = PROJECT_ROOT / "knowledge_base"
FRONTEND_PATH = PROJECT_ROOT / "frontend"

load_dotenv(dotenv_path=ENV_PATH)

app = FastAPI(title="AI Nõustamisplatvorm")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

documents = load_knowledge_base(str(KB_PATH))
rag = SimpleRAG(documents)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# Staatiliste failide teenindamine
app.mount("/static", StaticFiles(directory=str(FRONTEND_PATH)), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_PATH / "index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "knowledge_base_documents": len(documents),
        "api_key_loaded": bool(api_key),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY puudub või .env faili ei loetud sisse."
        )

    results = rag.search(request.question, top_k=3)

    contexts = [item["document"]["content"] for item in results]
    filenames = [item["document"]["filename"] for item in results]

    print("Kasutaja küsimus:", request.question)
    for item in results:
        print(
            "Leitud:",
            item["document"]["filename"],
            "| chunk:",
            item["document"]["chunk_id"],
            "| score:",
            round(item["score"], 3),
        )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(request.question, contexts)},
        ],
        temperature=0.4,
    )

    answer = response.choices[0].message.content or ""

    return ChatResponse(
        answer=answer,
        retrieved_context=filenames,
    )