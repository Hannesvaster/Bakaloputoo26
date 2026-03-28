import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

from app.kb_loader import load_knowledge_base
from app.models import ChatRequest, ChatResponse
from app.prompts import SYSTEM_PROMPT, build_user_prompt
from app.rag import SimpleRAG

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
ENV_PATH = BASE_DIR.parent / ".env"
KB_PATH = PROJECT_ROOT / "knowledge_base"

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
client = OpenAI(api_key=api_key)


@app.get("/")
def root():
    return {
        "message": "AI nõustamisplatvorm töötab",
        "knowledge_base_documents": len(documents),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
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