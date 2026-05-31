import asyncio
import json
from typing import Any

from fastapi import WebSocket


class ChatHub:
    def __init__(self) -> None:
        self._rooms: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._rooms.setdefault(session_id, set()).add(websocket)

    async def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            room = self._rooms.get(session_id)
            if not room:
                return
            room.discard(websocket)
            if not room:
                self._rooms.pop(session_id, None)

    async def broadcast(self, session_id: str, payload: dict[str, Any]) -> None:
        async with self._lock:
            room = list(self._rooms.get(session_id, set()))

        dead: list[WebSocket] = []
        data = json.dumps(payload, ensure_ascii=False)
        for ws in room:
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)

        if dead:
            async with self._lock:
                room_set = self._rooms.get(session_id)
                if room_set:
                    for ws in dead:
                        room_set.discard(ws)


chat_hub = ChatHub()
