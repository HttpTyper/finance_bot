from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Case
from services import case_service
from keyboards.inline import main_menu_kb, cases_list_kb, admin_menu_kb, back_kb

router = Router()

AUDIT_TITLES = [
    "Ликвидность: оценка платёжеспособности",
    "Рентабельность: анализ эффективности",
    "Финансовая устойчивость и риск банкротства",
    "Оборачиваемость: деловая активность",
    "Аудит денежных потоков (ДДС)",
]


async def get_or_create_user(message: types.Message, db: AsyncSession) -> User:
    user = await case_service.get_user_by_tg(db, message.from_user.id)
    if not user:
        from config import ADMIN_IDS
        is_admin = message.from_user.id in ADMIN_IDS
        user = await case_service.create_user(
            db,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        user.is_admin = is_admin
    return user


@router.message(CommandStart())
async def cmd_start(message: types.Message, db: AsyncSession):
    user = await get_or_create_user(message, db)
    await message.answer(
        f"👋 <b>Добро пожаловать, {user.full_name or 'пользователь'}!</b>\n\n"
        "Это симулятор кейсов по реальному сектору экономики.\n"
        "Вы будете анализировать финансовые отчёты компаний\n"
        "и принимать управленческие решения.\n\n"
        "Выберите действие в меню:",
        reply_markup=main_menu_kb(user.is_admin),
    )


@router.message(Command("menu"))
async def cmd_menu(message: types.Message, db: AsyncSession):
    user = await case_service.get_user_by_tg(db, message.from_user.id)
    is_admin = user.is_admin if user else False
    await message.answer("Главное меню:", reply_markup=main_menu_kb(is_admin))


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(callback: types.CallbackQuery, db: AsyncSession):
    user = await case_service.get_user_by_tg(db, callback.from_user.id)
    is_admin = user.is_admin if user else False
    await callback.message.edit_text(
        "Главное меню:", reply_markup=main_menu_kb(is_admin)
    )
    await callback.answer()


@router.callback_query(F.data == "menu:cases")
async def cb_cases_list(callback: types.CallbackQuery, db: AsyncSession):
    cases = [c for c in await case_service.get_all_cases(db) if c.industry != "audit"]
    if not cases:
        await callback.message.edit_text(
            "📭 Пока нет доступных кейсов. Скоро появятся!",
            reply_markup=cases_list_kb([]),
        )
        await callback.answer()
        return
    await callback.message.edit_text(
        "📂 <b>Доступные кейсы</b>\n\nВыберите кейс для изучения:",
        reply_markup=cases_list_kb(cases),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:profile")
async def cb_profile(callback: types.CallbackQuery, db: AsyncSession):
    user = await case_service.get_user_by_tg(db, callback.from_user.id)
    if not user:
        await callback.answer("Сначала введите /start", show_alert=True)
        return
    position = await case_service.get_user_rating_position(db, user.id)
    await callback.message.edit_text(
        f"👤 <b>Мой профиль</b>\n\n"
        f"Имя: {user.full_name or '—'}\n"
        f"Рейтинг: {user.rating:.1f}\n"
        f"Кейсов пройдено: {user.cases_completed}\n"
        f"Место в рейтинге: #{position}\n"
        f"Админ: {'✅' if user.is_admin else '❌'}",
        reply_markup=back_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:rating")
async def cb_rating(callback: types.CallbackQuery, db: AsyncSession):
    top = await case_service.get_leaderboard(db)
    lines = ["🏆 <b>Топ пользователей</b>\n"]
    for i, u in enumerate(top, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
        lines.append(f"{medal} {u.full_name or '—'} — {u.rating:.1f}")
    if not top:
        lines.append("Пока нет данных.")
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=back_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:admin")
async def cb_admin_menu(callback: types.CallbackQuery, db: AsyncSession):
    user = await case_service.get_user_by_tg(db, callback.from_user.id)
    if not user or not user.is_admin:
        await callback.answer("Нет доступа", show_alert=True)
        return
    await callback.message.edit_text(
        "🛠 <b>Админ панель</b>",
        reply_markup=admin_menu_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "menu:audit")
async def cb_audit_menu(callback: types.CallbackQuery, db: AsyncSession):
    from keyboards.inline import audit_menu_kb
    await callback.message.edit_text(
        "📚 <b>Обучение аудиту</b>\n\n"
        "Выберите тему для изучения. Каждый модуль содержит "
        "теоретические вопросы, расчёт коэффициентов и "
        "аудиторские процедуры на основе учебника «Основы аудита».\n\n"
        "После прохождения всех шагов вы получите оценку.",
        reply_markup=audit_menu_kb(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("case:audit:"))
async def cb_audit_case(callback: types.CallbackQuery, db: AsyncSession):
    try:
        index = int(callback.data.split(":")[2]) - 1
        if index < 0 or index >= len(AUDIT_TITLES):
            await callback.answer("Тема не найдена", show_alert=True)
            return
        title = AUDIT_TITLES[index]
        result = await db.execute(
            select(Case).where(Case.title == title)
        )
        case = result.scalar_one_or_none()
        if not case:
            await callback.answer("Кейс не загружен", show_alert=True)
            return

        user = await case_service.get_user_by_tg(db, callback.from_user.id)
        if not user:
            await callback.answer("Сначала введите /start", show_alert=True)
            return

        from keyboards.inline import confirm_case_kb
        existing = await case_service.get_active_session(db, user.id, case.id)
        if existing:
            await callback.message.edit_text(
                f"📘 <b>{case.title}</b>\n\n"
                f"{case.preamble}\n\n"
                f"Уровень: {case.difficulty.value}\n\n"
                f"⚠️ У вас есть незавершённая сессия.\n"
                f"Можете продолжить или начать заново.",
                reply_markup=confirm_case_kb(case.id, has_session=True),
            )
        else:
            await callback.message.edit_text(
                f"📘 <b>{case.title}</b>\n\n"
                f"{case.preamble}\n\n"
                f"Уровень: {case.difficulty.value}\n"
                f"Готовы начать?",
                reply_markup=confirm_case_kb(case.id),
            )
        await callback.answer()
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Ошибка при открытии аудит-кейса")
        await callback.answer("Ошибка", show_alert=True)
