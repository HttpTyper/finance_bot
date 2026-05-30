import datetime

from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession

from services import case_service
from services.engine import GameEngine, INITIAL_STATE
from keyboards.inline import (
    confirm_case_kb, options_kb, finish_kb, format_options_text,
)

router = Router()


@router.callback_query(F.data.startswith("case:info:"))
async def cb_case_info(callback: types.CallbackQuery, db: AsyncSession):
    case_id = int(callback.data.split(":")[2])
    case = await case_service.get_case_by_id(db, case_id)
    if not case:
        await callback.answer("Кейс не найден", show_alert=True)
        return

    user = await case_service.get_user_by_tg(db, callback.from_user.id)
    if not user:
        await callback.answer("Сначала введите /start", show_alert=True)
        return

    existing = await case_service.get_active_session(db, user.id, case_id)
    if existing:
        await callback.message.edit_text(
            f"📘 <b>{case.title}</b>\n\n"
            f"{case.preamble}\n\n"
            f"Уровень: {case.difficulty.value}\n\n"
            f"⚠️ У вас есть незавершённая сессия.\n"
            f"Можете продолжить или начать заново.",
            reply_markup=confirm_case_kb(case_id, has_session=True),
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"📘 <b>{case.title}</b>\n\n"
        f"{case.preamble}\n\n"
        f"Уровень: {case.difficulty.value}\n"
        f"Готовы начать?",
        reply_markup=confirm_case_kb(case_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("case:restart:"))
async def cb_case_restart(callback: types.CallbackQuery, db: AsyncSession):
    try:
        await callback.answer()
    except Exception:
        pass

    try:
        case_id = int(callback.data.split(":")[2])
        user = await case_service.get_user_by_tg(db, callback.from_user.id)
        if not user:
            return

        old_session = await case_service.get_active_session(db, user.id, case_id)
        if old_session:
            await case_service.complete_session(db, old_session)

        case = await case_service.get_case_with_steps(db, case_id)
        if not case or not case.steps:
            return

        session_state = dict(INITIAL_STATE)
        session_state["health"] = max(0, 100 - len(case.steps) * 20)
        session_obj = await case_service.create_session(
            db, user.id, case_id, session_state
        )

        engine = GameEngine(case, session_obj)
        step = engine.get_current_step()
        if not step:
            return

        text = engine.get_progress_text() + "\n\n"
        if step.data_snapshot:
            text += engine.get_step_data_text(step) + "\n"
        text += engine.get_question_text(step)
        text += "\n\n<b>Варианты ответов:</b>\n" + format_options_text(step.options)

        await callback.message.edit_text(
            text,
            reply_markup=options_kb(step.options, step.id),
        )
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Ошибка при перезапуске кейса")


@router.callback_query(F.data.startswith("case:play:"))
async def cb_case_play(callback: types.CallbackQuery, db: AsyncSession):
    try:
        await callback.answer()
    except Exception:
        pass

    try:
        case_id = int(callback.data.split(":")[2])
        user = await case_service.get_user_by_tg(db, callback.from_user.id)
        if not user:
            return

        case = await case_service.get_case_with_steps(db, case_id)
        if not case or not case.steps:
            return

        existing = await case_service.get_active_session(db, user.id, case_id)
        if existing:
            session_obj = existing
        else:
            session_state = dict(INITIAL_STATE)
            session_state["health"] = max(0, 100 - len(case.steps) * 20)
            session_obj = await case_service.create_session(
                db, user.id, case_id, session_state
            )

        engine = GameEngine(case, session_obj)
        step = engine.get_current_step()
        if not step:
            return

        text = engine.get_progress_text() + "\n\n"
        if step.data_snapshot:
            text += engine.get_step_data_text(step) + "\n"
        text += engine.get_question_text(step)
        text += "\n\n<b>Варианты ответов:</b>\n" + format_options_text(step.options)

        await callback.message.edit_text(
            text,
            reply_markup=options_kb(step.options, step.id),
        )
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Ошибка при старте кейса")


@router.callback_query(F.data.startswith("step:answer:"))
async def cb_step_answer(callback: types.CallbackQuery, db: AsyncSession):
    import logging
    logger = logging.getLogger(__name__)
    try:
        await callback.answer()
    except Exception:
        pass

    try:
        parts = callback.data.split(":")
        step_id, option_id = int(parts[2]), int(parts[3])
        logger.info(f"Ответ: шаг {step_id}, вариант {option_id}")

        option = await case_service.get_option_by_id(db, option_id)
        if not option:
            await callback.message.answer("❌ Ошибка: вариант не найден")
            return

        user = await case_service.get_user_by_tg(db, callback.from_user.id)
        if not user:
            await callback.message.answer("❌ Сначала введите /start")
            return

        step = await case_service.get_step_with_options(db, step_id)
        if not step:
            await callback.message.answer("❌ Шаг не найден")
            return

        session_obj = await case_service.get_active_session(db, user.id, step.case_id)
        if not session_obj:
            await callback.message.answer("❌ Сессия не найдена. Начните заново.")
            return

        case = await case_service.get_case_with_steps(db, step.case_id)
        engine = GameEngine(case, session_obj)

        is_correct = engine.check_answer(option)
        engine.apply_answer(option)

        await case_service.save_answer(db, session_obj.id, step_id, option_id, is_correct)
        await case_service.update_session(db, session_obj)

        result_icon = "✅" if is_correct else "❌"
        text = f"{result_icon} <b>{'Верно!' if is_correct else 'Неверно'}</b>\n\n"
        text += f"<i>{option.explanation}</i>\n\n"
        text += engine.get_progress_text() + "\n\n"

        if engine.is_finished:
            text += engine.get_result_text()
            session_obj.completed_at = datetime.datetime.utcnow()
            user.rating += 10 * (engine.session.correct_answers / max(engine.session.total_answers, 1))
            user.cases_completed += 1
            await case_service.update_session(db, session_obj)
            await case_service.update_user(db, user)
            await callback.message.edit_text(text, reply_markup=finish_kb())
        else:
            next_step = engine.steps[engine.session.current_step]
            if next_step.data_snapshot:
                text += "📊 <b>Новые данные:</b>\n"
                text += engine.get_step_data_text(next_step)
                text += "\n"
            text += f"<b>{next_step.question}</b>"
            text += "\n\n<b>Варианты ответов:</b>\n" + format_options_text(next_step.options)
            await callback.message.edit_text(
                text,
                reply_markup=options_kb(next_step.options, next_step.id),
            )

    except Exception:
        logger.exception("Ошибка при обработке ответа")
        try:
            await callback.message.answer("❌ Произошла ошибка. Начните кейс заново через /start")
        except Exception:
            pass
