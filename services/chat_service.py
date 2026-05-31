import aiohttp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_IDS, BOT_TOKEN
from database.models import ChatMessage, ChatSession

WELCOME_TEXT = (
    "Здравствуйте! Это поддержка Finance Simulator. "
    "Напишите вопрос — мы ответим здесь или подскажем, как пользоваться ботом."
)


def message_to_dict(msg: ChatMessage) -> dict:
    return {
        "id": msg.id,
        "session_id": msg.session_id,
        "role": msg.role,
        "text": msg.text,
        "created_at": msg.created_at.isoformat() + "Z",
    }


async def get_or_create_session(db: AsyncSession, session_id: str, visitor_name: str | None = None) -> ChatSession:
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    chat_session = result.scalar_one_or_none()
    if chat_session:
        if visitor_name and not chat_session.visitor_name:
            chat_session.visitor_name = visitor_name
            await db.commit()
        return chat_session

    chat_session = ChatSession(id=session_id, visitor_name=visitor_name or None)
    db.add(chat_session)
    await db.commit()
    await db.refresh(chat_session)
    return chat_session


async def get_messages(db: AsyncSession, session_id: str) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    return list(result.scalars().all())


async def ensure_welcome(db: AsyncSession, session_id: str) -> ChatMessage | None:
    messages = await get_messages(db, session_id)
    if messages:
        return None
    msg = ChatMessage(session_id=session_id, role="support", text=WELCOME_TEXT)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def add_message(
    db: AsyncSession,
    session_id: str,
    role: str,
    text: str,
    visitor_name: str | None = None,
) -> ChatMessage:
    await get_or_create_session(db, session_id, visitor_name)
    msg = ChatMessage(session_id=session_id, role=role, text=text.strip())
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    if role == "visitor":
        await notify_admins(session_id, text.strip(), visitor_name)

    return msg


async def add_support_reply(db: AsyncSession, session_id: str, text: str) -> ChatMessage:
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    if not result.scalar_one_or_none():
        raise ValueError("Session not found")

    msg = ChatMessage(session_id=session_id, role="support", text=text.strip())
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def notify_admins(session_id: str, text: str, visitor_name: str | None) -> None:
    if not BOT_TOKEN or not ADMIN_IDS:
        return

    name = visitor_name or "Посетитель"
    body = (
        f"💬 <b>Новое сообщение с сайта</b>\n\n"
        f"От: {name}\n"
        f"Сессия: <code>{session_id[:8]}…</code>\n\n"
        f"{text}"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    async with aiohttp.ClientSession() as http:
        for admin_id in ADMIN_IDS:
            try:
                await http.post(url, json={
                    "chat_id": admin_id,
                    "text": body,
                    "parse_mode": "HTML",
                })
            except Exception:
                pass
