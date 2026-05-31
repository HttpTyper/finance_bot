import os
import sys
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from audit_cases import AUDIT_CASES
from game_cases import GAME_CASES
from database.db import async_session, init_db
from database import models  # noqa: F401 — register ORM models
from services.chat_hub import chat_hub
from services import chat_service

all_cases = []


def collect_cases():
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
    await init_db()
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


class ChatSendRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    visitor_name: str | None = Field(default=None, max_length=128)


class AdminReplyRequest(BaseModel):
    session_id: str
    text: str = Field(min_length=1, max_length=2000)
    secret: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/chat/sessions/{session_id}/messages")
async def chat_history(session_id: str):
    async with async_session() as db:
        await chat_service.get_or_create_session(db, session_id)
        welcome = await chat_service.ensure_welcome(db, session_id)
        messages = await chat_service.get_messages(db, session_id)

    payload = [chat_service.message_to_dict(m) for m in messages]
    return {"session_id": session_id, "messages": payload, "welcome_sent": welcome is not None}


@app.post("/api/chat/sessions/{session_id}/messages")
async def chat_send(session_id: str, body: ChatSendRequest):
    async with async_session() as db:
        msg = await chat_service.add_message(
            db, session_id, "visitor", body.text, body.visitor_name
        )

    data = {"type": "message", "message": chat_service.message_to_dict(msg)}
    await chat_hub.broadcast(session_id, data)
    return data["message"]


@app.post("/api/chat/admin/reply")
async def chat_admin_reply(body: AdminReplyRequest):
    from config import CHAT_ADMIN_SECRET

    if not CHAT_ADMIN_SECRET or body.secret != CHAT_ADMIN_SECRET:
        raise HTTPException(403, "Forbidden")

    try:
        async with async_session() as db:
            msg = await chat_service.add_support_reply(db, body.session_id, body.text)
    except ValueError:
        raise HTTPException(404, "Session not found")

    data = {"type": "message", "message": chat_service.message_to_dict(msg)}
    await chat_hub.broadcast(body.session_id, data)
    return data["message"]


@app.websocket("/api/chat/ws/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    await chat_hub.connect(session_id, websocket)

    try:
        async with async_session() as db:
            await chat_service.get_or_create_session(db, session_id)
            welcome = await chat_service.ensure_welcome(db, session_id)
            messages = await chat_service.get_messages(db, session_id)

        await websocket.send_json({
            "type": "history",
            "messages": [chat_service.message_to_dict(m) for m in messages],
        })

        while True:
            raw = await websocket.receive_json()
            text = (raw.get("text") or "").strip()
            if not text:
                continue

            visitor_name = raw.get("visitor_name")
            async with async_session() as db:
                msg = await chat_service.add_message(
                    db, session_id, "visitor", text, visitor_name
                )

            payload = {"type": "message", "message": chat_service.message_to_dict(msg)}
            await chat_hub.broadcast(session_id, payload)

    except WebSocketDisconnect:
        pass
    finally:
        await chat_hub.disconnect(session_id, websocket)


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
