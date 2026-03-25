import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI

from app.models import ChatRequest, ChatResponse
from app.kb_loader import load_knowledge_base
from app.rag import SimpleRAG
from app.prompts import SYSTEM_PROMPT, build_user_prompt

load_dotenv()

app = FastAPI(title="AI Nõustamisplatvorm")

BASE_DIR = Path(__file__).resolve().parent
KB_PATH = BASE_DIR.parent.parent / "knowledge_base"

documents = load_knowledge_base(str(KB_PATH))
rag = SimpleRAG(documents)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.get("/")
def root():
    return {"message": "AI nõustamisplatvorm töötab"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    results = rag.search(request.question, top_k=3)
    contexts = [r["document"]["content"] for r in results]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(request.question, contexts)},
        ],
        temperature=0.4,
    )

    answer = response.choices[0].message.content

    return ChatResponse(
        answer=answer,
        retrieved_context=[r["document"]["filename"] for r in results],
    )