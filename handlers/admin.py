from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from services import case_service
from keyboards.inline import admin_menu_kb

router = Router()


class LoadCaseStates(StatesGroup):
    waiting_for_json = State()


@router.callback_query(F.data == "admin:cases")
async def cb_admin_cases(callback: types.CallbackQuery, db: AsyncSession):
    user = await case_service.get_user_by_tg(db, callback.from_user.id)
    if not user or not user.is_admin:
        await callback.answer("Нет доступа", show_alert=True)
        return
    cases = await case_service.get_all_cases(db)
    text_lines = ["📂 <b>Все кейсы</b>\n"]
    for c in cases:
        steps_count = len(c.steps) if hasattr(c, 'steps') and c.steps else 0
        text_lines.append(f"• #{c.id} <b>{c.title}</b> ({c.difficulty.value}) — {steps_count} шагов")
    if not cases:
        text_lines.append("Кейсов пока нет.")
    await callback.message.edit_text(
        "\n".join(text_lines),
        reply_markup=admin_menu_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:load_case")
async def cb_admin_load_case(callback: types.CallbackQuery, state: FSMContext, db: AsyncSession):
    user = await case_service.get_user_by_tg(db, callback.from_user.id)
    if not user or not user.is_admin:
        await callback.answer("Нет доступа", show_alert=True)
        return
    await callback.message.edit_text(
        "📄 Отправьте JSON с описанием кейса.\n\n"
        "Формат:\n"
        "<pre>{\n"
        '  "title": "...",\n'
        '  "description": "...",\n'
        '  "preamble": "...",\n'
        '  "difficulty": "easy|medium|hard",\n'
        '  "steps": [\n'
        "    {\n"
        '      "order": 1,\n'
        '      "title": "...",\n'
        '      "data_snapshot": {"tables": [...]},\n'
        '      "question": "...",\n'
        '      "options": [\n'
        '        {"text": "...", "is_correct": true, "explanation": "...", "effects": {...}}\n'
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}</pre>",
        reply_markup=admin_menu_kb(),
    )
    await state.set_state(LoadCaseStates.waiting_for_json)
    await callback.answer()


@router.message(LoadCaseStates.waiting_for_json)
async def handle_case_json(message: types.Message, state: FSMContext, db: AsyncSession):
    import json
    try:
        data = json.loads(message.text)
    except json.JSONDecodeError:
        await message.answer("❌ Ошибка: невалидный JSON. Попробуйте снова.")
        return

    case_obj = await case_service.create_case_from_json(db, data)
    await message.answer(
        f"✅ Кейс «{case_obj.title}» успешно загружен! (ID: {case_obj.id})"
    )
    await state.clear()
