from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Case
from services import case_service
from keyboards.inline import main_menu_kb, cases_list_kb, admin_menu_kb, back_kb

router = Router()

def case_to_idx(case_index: int) -> int:
    """Convert 1-based case index (1-5, 7-16) to 0-based list index in AUDIT_TITLES/AUDIT_CASES.
    Case index 6 (MCA, THEORY_ONLY) is never passed here."""
    if case_index <= 5:
        return case_index - 1
    else:
        return case_index - 2  # skip gap at index 6

AUDIT_TITLES = [
    "Ликвидность: оценка платёжеспособности",
    "Рентабельность: анализ эффективности",
    "Финансовая устойчивость и риск банкротства",
    "Оборачиваемость: деловая активность",
    "Аудит денежных потоков (ДДС)",
    "Аудиторское заключение: виды и формирование",
    "Система внутреннего контроля (СВК): оценка и тестирование",
    "Профессиональная этика аудитора",
    "Существенность в аудите",
    "Планирование аудита",
    "Аудит основных средств",
    "Аудит заёмных средств и кредитов",
    "Аудит выручки и расходов",
    "Мошенничество в аудите",
    "Сопутствующие аудиту услуги",
]

THEORY_ONLY = {
    6: {
        "title": "Основы МСА: стандарты аудита",
        "theory": (
            "<b>Обзор международных стандартов аудита (МСА)</b>\n\n"
            "МСА — единые требования к проведению аудита, признанные в РФ.\n\n"
            "🔹 <b>МСА 200</b> — Основные цели аудитора\n"
            "Аудитор должен получить разумную уверенность в отсутствии существенных искажений.\n\n"
            "🔹 <b>МСА 300</b> — Планирование аудита\n"
            "Аудитор разрабатывает общую стратегию и детальный план проверки.\n\n"
            "🔹 <b>МСА 315</b> (пересм. 2019) — Оценка рисков\n"
            "Выявление и оценка рисков существенного искажения на уровне "
            "финансовой отчётности и на уровне предпосылок.\n\n"
            "🔹 <b>МСА 500</b> — Аудиторские доказательства\n"
            "Определяет виды доказательств и процедуры их получения "
            "(инспектирование, наблюдение, запрос, подтверждение, пересчёт, "
            "аналитические процедуры).\n\n"
            "🔹 <b>МСА 520</b> — Аналитические процедуры\n"
            "Обязательны на этапах ответной реакции на риски и завершения аудита.\n\n"
            "🔹 <b>МСА 570</b> — Непрерывность деятельности\n"
            "Оценка способности компании продолжать деятельность.\n\n"
            "🔹 <b>МСА 700</b> — Формирование мнения и заключение\n"
            "Виды мнений: немодифицированное, модифицированное "
            "(оговорка, отрицательное, отказ от выражения)."
        ),
        "theory_page_2": (
            "<b>Применение МСА на практике</b>\n\n"
            "📊 <b>Этапы аудита и соответствующие МСА (табл. 7.9 учебника):</b>\n\n"
            "1️⃣ <b>Оценка рисков:</b>\n"
            "• МСА 315 — аналитические процедуры для выявления рисков\n"
            "• МСА 240 — недобросовестные действия\n\n"
            "2️⃣ <b>Ответная реакция на риски:</b>\n"
            "• МСА 330 — аудиторские процедуры в ответ на риски\n"
            "• МСА 520 — аналитические процедуры\n"
            "• МСА 240 — процедуры в отношении мошенничества\n\n"
            "3️⃣ <b>Завершающий этап:</b>\n"
            "• МСА 520 — итоговые аналитические процедуры\n"
            "• МСА 570 — оценка непрерывности деятельности\n"
            "• МСА 700 — формирование мнения\n\n"
            "⚠️ <b>Ключевые понятия:</b>\n"
            "• Существенность (материальность) — информация считается "
            "существенной, если её пропуск или искажение может повлиять "
            "на решения пользователей отчётности\n"
            "• Аудиторский риск = Неотъемлемый риск × Риск СВК × Риск необнаружения\n"
            "• Аудиторские доказательства — информация, полученная аудитором "
            "при проведении процедур\n\n"
            "📖 Учебник: темы 1–7, табл. 7.8–7.12"
        ),
    }
}


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
    from config import LANDING_URL

    text = (
        f"👋 <b>Добро пожаловать, {user.full_name or 'пользователь'}!</b>\n\n"
        "Это симулятор кейсов по реальному сектору экономики.\n"
        "Вы будете анализировать финансовые отчёты компаний\n"
        "и принимать управленческие решения.\n\n"
    )
    if LANDING_URL:
        text += f'Подробнее о проекте: <a href="{LANDING_URL}">сайт</a>\n\n'
    text += "Выберите действие в меню:"
    await message.answer(
        text,
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


@router.callback_query(F.data.startswith("case:audit:theory:"))
async def cb_audit_theory(callback: types.CallbackQuery, db: AsyncSession):
    try:
        index = int(callback.data.split(":")[3])

        from keyboards.inline import theory_kb

        if index == 6:
            data = THEORY_ONLY.get(index, {})
            text = f"📖 <b>{data.get('title', 'Основы МСА')}</b>\n\n{data.get('theory', '')}"
            await callback.message.edit_text(text, reply_markup=theory_kb(index, has_page_2=True, has_quiz=False))
            await callback.answer()
            return

        if index < 1 or index > 16:
            await callback.answer("Тема не найдена", show_alert=True)
            return
        title = AUDIT_TITLES[case_to_idx(index)]
        result = await db.execute(select(Case).where(Case.title == title))
        case = result.scalar_one_or_none()
        if not case:
            await callback.answer("Кейс не загружен", show_alert=True)
            return

        from audit_cases import AUDIT_CASES
        case_data = AUDIT_CASES[case_to_idx(index)]
        theory = case_data.get("theory", "")
        text = f"📖 <b>{case.title}</b>\n\n{theory}"
        await callback.message.edit_text(text, reply_markup=theory_kb(index, has_page_2=True, has_quiz=True))
        await callback.answer()
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Ошибка при показе теории")
        await callback.answer("Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("audit:theory:page2:"))
async def cb_audit_theory_page2(callback: types.CallbackQuery, db: AsyncSession):
    try:
        index = int(callback.data.split(":")[3])

        from keyboards.inline import theory_page2_kb

        if index == 6:
            data = THEORY_ONLY.get(index, {})
            text = f"📖 <b>{data.get('title', 'Основы МСА')}</b>\n\n{data.get('theory_page_2', '')}"
            await callback.message.edit_text(text, reply_markup=theory_page2_kb(index, has_quiz=False))
            await callback.answer()
            return

        from audit_cases import AUDIT_CASES
        case_data = AUDIT_CASES[case_to_idx(index)]
        theory2 = case_data.get("theory_page_2", "")
        quiz = case_data.get("theory_quiz", [])
        text = f"📖 <b>Применение в аудите</b>\n\n{theory2}"
        await callback.message.edit_text(text, reply_markup=theory_page2_kb(index, has_quiz=len(quiz) > 0))
        await callback.answer()
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Ошибка при показе теории (стр.2)")
        await callback.answer("Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("audit:quiz:answer:"))
async def cb_audit_quiz_answer(callback: types.CallbackQuery, db: AsyncSession):
    try:
        parts = callback.data.split(":")
        case_index = int(parts[3])
        q_index = int(parts[4])
        opt_index = int(parts[5])

        from audit_cases import AUDIT_CASES
        case_data = AUDIT_CASES[case_to_idx(case_index)]
        quiz = case_data.get("theory_quiz", [])
        if q_index >= len(quiz):
            await callback.answer("Вопрос не найден", show_alert=True)
            return

        question = quiz[q_index]
        option = question["options"][opt_index]
        is_correct = option["is_correct"]
        icon = "✅" if is_correct else "❌"
        text = f"{icon} <b>{'Верно!' if is_correct else 'Неверно'}</b>\n\n"
        text += f"<i>{option['explanation']}</i>"

        from keyboards.inline import back_kb
        from aiogram.utils.keyboard import InlineKeyboardBuilder

        total = len(quiz)
        if q_index + 1 < total:
            text += "\n\n👇 <b>Следующий вопрос</b>"
            builder = InlineKeyboardBuilder()
            builder.button(text="Далее →", callback_data=f"audit:quiz:{q_index + 1}:{case_index}")
            builder.button(text="← Назад", callback_data="menu:audit")
            builder.adjust(1)
            await callback.message.edit_text(text, reply_markup=builder.as_markup())
        else:
            label = "📖 К вопросам" if case_index != 6 else "← В меню"
            cb = f"case:audit:start:{case_index}" if case_index != 6 else "menu:audit"
            text += f"\n\n<b>Теория изучена!</b> Переходите к вопросам."
            await callback.message.edit_text(text, reply_markup=back_kb(cb, label))
        await callback.answer()
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Ошибка при ответе на вопрос теории")
        await callback.answer("Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("audit:quiz:"))
async def cb_audit_quiz(callback: types.CallbackQuery, db: AsyncSession):
    try:
        parts = callback.data.split(":")
        q_index = int(parts[2])
        case_index = int(parts[3])

        from keyboards.inline import theory_quiz_kb

        if case_index == 6:
            from keyboards.inline import back_kb
            await callback.message.edit_text(
                "Это ознакомительный раздел. Вопросов нет.",
                reply_markup=back_kb("menu:audit", "← В меню")
            )
            await callback.answer()
            return

        from audit_cases import AUDIT_CASES
        case_data = AUDIT_CASES[case_to_idx(case_index)]
        quiz = case_data.get("theory_quiz", [])

        if not quiz or q_index >= len(quiz):
            title = AUDIT_TITLES[case_to_idx(case_index)]
            text = f"📖 <b>{title}</b>\n\nТеория изучена! Переходите к вопросам."
            from keyboards.inline import back_kb
            await callback.message.edit_text(text, reply_markup=back_kb(f"case:audit:start:{case_index}", "📖 К вопросам"))
            await callback.answer()
            return

        question = quiz[q_index]
        text = f"❓ <b>Вопрос {q_index + 1} из {len(quiz)}</b>\n\n{question['question']}"
        opts_text = "\n\n".join(f"{i + 1}. {o['text']}" for i, o in enumerate(question['options']))
        text += f"\n\n<b>Варианты ответов:</b>\n{opts_text}"
        await callback.message.edit_text(text, reply_markup=theory_quiz_kb(case_index, q_index, question['options']))
        await callback.answer()
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Ошибка при показе вопроса теории")
        await callback.answer("Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("case:audit:start:"))
async def cb_audit_case(callback: types.CallbackQuery, db: AsyncSession):
    try:
        case_idx = int(callback.data.split(":")[3])
        if case_idx == 6:
            await callback.answer("Этот раздел не имеет кейса", show_alert=True)
            return
        list_idx = case_to_idx(case_idx)
        if list_idx < 0 or list_idx >= len(AUDIT_TITLES):
            await callback.answer("Тема не найдена", show_alert=True)
            return
        title = AUDIT_TITLES[list_idx]
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
