from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def main_menu_kb(is_admin: bool = False):
    builder = InlineKeyboardBuilder()
    builder.button(text="Доступные кейсы", callback_data="menu:cases")
    builder.button(text="Обучение аудиту", callback_data="menu:audit")
    builder.button(text="Мой профиль", callback_data="menu:profile")
    builder.button(text="Рейтинг", callback_data="menu:rating")
    if is_admin:
        builder.button(text="Админ панель", callback_data="menu:admin")
    builder.adjust(1)
    return builder.as_markup()


def audit_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Ликвидность: оценка платёжеспособности", callback_data="case:audit:1")
    builder.button(text="Рентабельность: анализ эффективности", callback_data="case:audit:2")
    builder.button(text="Финансовая устойчивость и риск банкротства", callback_data="case:audit:3")
    builder.button(text="Оборачиваемость: деловая активность", callback_data="case:audit:4")
    builder.button(text="Аудит денежных потоков (ДДС)", callback_data="case:audit:5")
    builder.button(text="Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def cases_list_kb(cases: list, page: int = 0):
    builder = InlineKeyboardBuilder()
    for case in cases:
        builder.button(
            text=f"{case.title} ({case.difficulty.value})",
            callback_data=f"case:info:{case.id}",
        )
    builder.button(text="Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()


def confirm_case_kb(case_id: int, has_session: bool = False):
    builder = InlineKeyboardBuilder()
    if has_session:
        builder.button(text="Продолжить", callback_data=f"case:play:{case_id}")
        builder.button(text="Начать заново", callback_data=f"case:restart:{case_id}")
    else:
        builder.button(text="Начать игру", callback_data=f"case:play:{case_id}")
    builder.button(text="Назад", callback_data="menu:cases")
    builder.adjust(1)
    return builder.as_markup()


def options_kb(options: list, step_id: int):
    builder = InlineKeyboardBuilder()
    for i, opt in enumerate(options, 1):
        builder.button(text=str(i), callback_data=f"step:answer:{step_id}:{opt.id}")
    builder.adjust(5 if len(options) <= 5 else 1)
    return builder.as_markup()


def format_options_text(options: list) -> str:
    lines = []
    for i, opt in enumerate(options, 1):
        lines.append(f"{i}. {opt.text}")
    return "\n\n".join(lines)


def back_kb(callback_data: str = "menu:main", text: str = "В меню"):
    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data=callback_data)
    return builder.as_markup()


def finish_kb():
    return back_kb()


def admin_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Список кейсов", callback_data="admin:cases")
    builder.button(text="Загрузить кейс (JSON)", callback_data="admin:load_case")
    builder.button(text="Назад", callback_data="menu:main")
    builder.adjust(1)
    return builder.as_markup()
