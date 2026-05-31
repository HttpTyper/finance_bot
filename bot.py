import asyncio
import logging
import os
from typing import Callable, Dict, Any, Awaitable

from aiohttp import web
from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import TelegramObject

from config import BOT_TOKEN
from database.db import init_db, async_session
from handlers import start, game, admin
from seed_data import seed_case
from audit_cases import AUDIT_CASES
from game_cases import GAME_CASES, seed_game_cases

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DbSessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with async_session() as session:
            data["db"] = session
            return await handler(event, data)


async def seed_audit_cases(session):
    from database.models import Case, Step, Option, Difficulty
    from sqlalchemy import select

    for case_data in AUDIT_CASES:
        result = await session.execute(
            select(Case).where(Case.title == case_data["title"])
        )
        if result.scalar_one_or_none():
            continue

        case = Case(
            title=case_data["title"],
            description=case_data["description"],
            preamble=case_data["preamble"],
            industry=case_data.get("industry", "audit"),
            difficulty=Difficulty(case_data["difficulty"]),
        )
        session.add(case)
        await session.flush()

        for sdata in case_data["steps"]:
            step = Step(
                case_id=case.id,
                order=sdata["order"],
                title=sdata.get("title", ""),
                data_snapshot=sdata.get("data_snapshot"),
                question=sdata["question"],
            )
            session.add(step)
            await session.flush()

            for odata in sdata["options"]:
                opt = Option(
                    step_id=step.id,
                    text=odata["text"],
                    is_correct=odata["is_correct"],
                    explanation=odata.get("explanation", ""),
                    effects=odata.get("effects"),
                )
                session.add(opt)

    await session.commit()


async def on_startup(bot: Bot):
    await init_db()
    logger.info("Database initialized")

    async with async_session() as session:
        await seed_case(session)
        await seed_audit_cases(session)
        await seed_game_cases(session)
        logger.info("Seed data loaded")


async def health_handler(_request: web.Request) -> web.Response:
    return web.Response(text="ok")


async def run_health_server() -> None:
    """Railway health checks expect a process listening on PORT."""
    port = int(os.getenv("PORT", "8080"))
    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/health", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info("Health server listening on port %s", port)


async def main():
    if not BOT_TOKEN:
        raise SystemExit(
            "BOT_TOKEN is not set. Add it in Railway → Service → Variables."
        )

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware())

    dp.include_router(start.router)
    dp.include_router(game.router)
    dp.include_router(admin.router)

    dp.startup.register(on_startup)

    await run_health_server()
    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
