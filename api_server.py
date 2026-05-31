"""
FastAPI-сервер для фронтенда лендинга.
Запуск: uvicorn api_server:app --reload --port 8081
"""

import sys
import os
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from audit_cases import AUDIT_CASES
from game_cases import GAME_CASES

all_cases = []


def collect_cases():
    """Собирает все кейсы из модулей."""
    result = []
    INDUSTRY_MAP = {"audit": "Аудит", "game": "Игра", "finance": "Финансы", "production": "Производство"}

    for i, c in enumerate(AUDIT_CASES):
        steps = []
        for s in c.get("steps", []) or c.get("steps_raw", []):
            steps.append({
                "order": s.get("order"),
                "title": s.get("title"),
                "question": s.get("question"),
                "data_snapshot": s.get("data_snapshot"),
                "options": [
                    {"index": j, "text": o["text"], "is_correct": o.get("is_correct", False)}
                    for j, o in enumerate(s.get("options", []))
                ],
            })
        raw_industry = c.get("industry", "audit")
        result.append({
            "id": i + 1,
            "title": c["title"],
            "description": c.get("description", ""),
            "industry": INDUSTRY_MAP.get(raw_industry, raw_industry),
            "difficulty": c.get("difficulty", "medium"),
            "preamble": c.get("preamble", ""),
            "theory": c.get("theory", ""),
            "theory_page_2": c.get("theory_page_2", ""),
            "steps": steps,
        })

    for i, c in enumerate(GAME_CASES):
        steps = []
        for s in c.get("steps", []) or c.get("steps_raw", []):
            steps.append({
                "order": s.get("order"),
                "title": s.get("title"),
                "question": s.get("question"),
                "data_snapshot": s.get("data_snapshot"),
                "options": [
                    {"index": j, "text": o["text"], "is_correct": o.get("is_correct", False)}
                    for j, o in enumerate(s.get("options", []))
                ],
            })
        raw_industry = c.get("industry", "game")
        result.append({
            "id": len(result) + 1,
            "title": c["title"],
            "description": c.get("description", ""),
            "industry": INDUSTRY_MAP.get(raw_industry, raw_industry),
            "difficulty": c.get("difficulty", "medium"),
            "preamble": c.get("preamble", ""),
            "steps": steps,
        })

    return result


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global all_cases
    all_cases = collect_cases()
    print(f"API: loaded {len(all_cases)} cases")
    yield


app = FastAPI(title="Finance Simulator API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnswerRequest(BaseModel):
    option_index: int


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/cases")
async def list_cases():
    return [
        {
            "id": c["id"],
            "title": c["title"],
            "description": c["description"],
            "industry": c["industry"],
            "difficulty": c["difficulty"],
        }
        for c in all_cases
    ]


@app.get("/api/cases/{case_id}")
async def get_case(case_id: int):
    for c in all_cases:
        if c["id"] == case_id:
            return c
    raise HTTPException(404, "Case not found")


@app.get("/api/cases/{case_id}/steps/{step_order}")
async def get_step(case_id: int, step_order: int):
    for c in all_cases:
        if c["id"] == case_id:
            for s in c["steps"]:
                if s["order"] == step_order:
                    return s
            raise HTTPException(404, "Step not found")
    raise HTTPException(404, "Case not found")


@app.post("/api/cases/{case_id}/steps/{step_order}/answer")
async def submit_answer(case_id: int, step_order: int, body: AnswerRequest):
    for c in all_cases:
        if c["id"] == case_id:
            for s in c["steps"]:
                if s["order"] == step_order:
                    opts = s["options"]
                    if body.option_index < 0 or body.option_index >= len(opts):
                        raise HTTPException(400, "Invalid option index")
                    chosen = opts[body.option_index]
                    return {
                        "correct": chosen["is_correct"],
                        "text": chosen["text"],
                        "explanation": chosen.get("explanation", ""),
                    }
            raise HTTPException(404, "Step not found")
    raise HTTPException(404, "Case not found")
