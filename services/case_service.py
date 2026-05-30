import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Case, Step, Option, User, Session, Answer, Difficulty


async def get_user_by_tg(db: AsyncSession, telegram_id: int) -> User | None:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, telegram_id: int, username: str = None, full_name: str = None) -> User:
    user = User(telegram_id=telegram_id, username=username, full_name=full_name)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_rating_position(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        select(User).order_by(User.rating.desc())
    )
    users = result.scalars().all()
    for i, u in enumerate(users, 1):
        if u.id == user_id:
            return i
    return 0


async def get_all_cases(db: AsyncSession, industry: str = None) -> list[Case]:
    query = select(Case).order_by(Case.id)
    if industry is not None:
        query = query.where(Case.industry == industry)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_case_by_id(db: AsyncSession, case_id: int) -> Case | None:
    result = await db.execute(select(Case).where(Case.id == case_id))
    return result.scalar_one_or_none()


async def get_case_with_steps(db: AsyncSession, case_id: int) -> Case | None:
    result = await db.execute(
        select(Case)
        .where(Case.id == case_id)
        .options(selectinload(Case.steps).selectinload(Step.options))
    )
    return result.scalar_one_or_none()


async def get_step_with_options(db: AsyncSession, step_id: int) -> Step | None:
    result = await db.execute(
        select(Step)
        .where(Step.id == step_id)
        .options(selectinload(Step.options))
    )
    return result.scalar_one_or_none()


async def get_option_by_id(db: AsyncSession, option_id: int) -> Option | None:
    result = await db.execute(select(Option).where(Option.id == option_id))
    return result.scalar_one_or_none()


async def create_session(db: AsyncSession, user_id: int, case_id: int, initial_state: dict) -> Session:
    session = Session(
        user_id=user_id,
        case_id=case_id,
        state=initial_state,
        current_step=0,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def complete_session(db: AsyncSession, session: Session):
    session.completed_at = datetime.datetime.utcnow()
    await db.merge(session)
    await db.commit()


async def get_active_session(db: AsyncSession, user_id: int, case_id: int) -> Session | None:
    result = await db.execute(
        select(Session).where(
            Session.user_id == user_id,
            Session.case_id == case_id,
            Session.completed_at.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def update_session(db: AsyncSession, session: Session):
    await db.merge(session)
    await db.commit()


async def update_user(db: AsyncSession, user: User):
    await db.merge(user)
    await db.commit()


async def save_answer(db: AsyncSession, session_id: int, step_id: int, option_id: int, is_correct: bool) -> Answer:
    answer = Answer(
        session_id=session_id,
        step_id=step_id,
        option_id=option_id,
        is_correct=is_correct,
    )
    db.add(answer)
    await db.commit()
    await db.refresh(answer)
    return answer


async def get_leaderboard(db: AsyncSession, limit: int = 10) -> list[User]:
    result = await db.execute(
        select(User).order_by(User.rating.desc()).limit(limit)
    )
    return list(result.scalars().all())


async def create_case_from_json(db: AsyncSession, data: dict) -> Case:
    case = Case(
        title=data["title"],
        description=data.get("description", ""),
        preamble=data.get("preamble", ""),
        industry=data.get("industry", ""),
        difficulty=Difficulty(data.get("difficulty", "medium")),
    )
    db.add(case)
    await db.flush()

    for sdata in data.get("steps", []):
        step = Step(
            case_id=case.id,
            order=sdata["order"],
            title=sdata.get("title", ""),
            data_snapshot=sdata.get("data_snapshot"),
            question=sdata["question"],
        )
        db.add(step)
        await db.flush()

        for odata in sdata.get("options", []):
            opt = Option(
                step_id=step.id,
                text=odata["text"],
                is_correct=odata.get("is_correct", False),
                explanation=odata.get("explanation", ""),
                effects=odata.get("effects"),
            )
            db.add(opt)

    await db.commit()
    await db.refresh(case)
    return case
