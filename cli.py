import os
import shutil
import sys
from dataclasses import dataclass
from typing import Any

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
os.system("chcp 65001 >nul 2>&1") if sys.platform == "win32" else None
sys.path.insert(0, os.path.dirname(__file__))

from audit_cases import AUDIT_CASES
from seed_data import CASE_JSON as DEMO_CASE


@dataclass
class Option:
    text: str
    is_correct: bool
    explanation: str
    effects: dict | None = None


@dataclass
class Step:
    order: int
    title: str
    question: str
    options: list[Option]
    data_snapshot: Any = None


@dataclass
class Case:
    title: str
    preamble: str
    difficulty: str
    steps: list[Step]


@dataclass
class Session:
    state: dict
    current_step: int = 0
    correct_answers: int = 0
    total_answers: int = 0


INITIAL_STATE = {
    "cash": 0, "receivables": 0, "inventory": 0, "payables": 0,
    "loan": 0, "equity": 0, "revenue": 0, "profit": 0,
    "total_assets": 0, "total_liabilities": 0, "health": 20,
    "step_results": [],
}


def fmt_title(text: str) -> str:
    w = shutil.get_terminal_size().columns
    return f"\n{'=' * w}\n{text.center(w)}\n{'=' * w}"


def fmt_table(data: dict) -> str:
    if not data or "tables" not in data:
        return ""
    lines = []
    for table in data["tables"]:
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        col_w = [max(len(str(r[i])) for r in [headers] + rows) + 2 for i in range(len(headers))]
        sep = "+" + "+".join("-" * w for w in col_w) + "+"
        hdr = "|" + "|".join(f" {h.center(col_w[i]-2)} " for i, h in enumerate(headers)) + "|"
        lines.extend([sep, hdr, sep])
        for row in rows:
            rl = "|" + "|".join(f" {str(row[i]).rjust(col_w[i]-2)} " if i < len(row) else " " * col_w[i] for i in range(len(headers))) + "|"
            lines.append(rl)
        lines.append(sep)
    return "\n".join(lines)


def fmt_state(state: dict) -> str:
    h = state.get("health", 0)
    bar_len = 20
    filled = round(h / 100 * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)
    return (
        f"\n  Деньги: {state.get('cash', 0):>10,} руб."
        f"\n  Выручка: {state.get('revenue', 0):>9,} руб."
        f"\n  Прибыль: {state.get('profit', 0):>9,} руб."
        f"\n  Здоровье: [{bar}] {h:.0f}%"
    )


def build_case(src: dict) -> Case:
    steps = []
    for s in src.get("steps", []):
        opts = [Option(**o) for o in s.get("options", [])]
        steps.append(Step(
            order=s["order"],
            title=s.get("title", ""),
            question=s["question"],
            options=opts,
            data_snapshot=s.get("data_snapshot"),
        ))
    return Case(
        title=src["title"],
        preamble=src.get("preamble", ""),
        difficulty=src.get("difficulty", "medium"),
        steps=steps,
    )


def show_progress(session: Session, total: int):
    results = session.state.get("step_results", [])
    dots = ""
    for i in range(total):
        dots += "🟢" if i < len(results) and results[i] else "🔴" if i < len(results) else "⚪"
    print(f"\n  Прогресс: {dots} ({len(results)}/{total})")


def play_case(case: Case):
    w = shutil.get_terminal_size().columns
    num_steps = len(case.steps)
    state = dict(INITIAL_STATE)
    state["health"] = max(0, 100 - num_steps * 20)
    session = Session(state=state)

    print(fmt_title(case.title))
    print(f"\n{case.preamble}\n")
    print(f"  Уровень: {case.difficulty.upper()}")
    print(f"  Шагов: {num_steps}")
    print(f"  Стартовое здоровье: {state['health']}%")
    input(f"\n{'─' * w}\nНажми Enter, чтобы начать...")

    for step in case.steps:
        os.system("cls" if os.name == "nt" else "clear")
        show_progress(session, num_steps)
        print(f"\n╔═══ ШАГ {step.order}/{num_steps} ═══╗")
        if step.title:
            print(f"║ {step.title}")
            print(f"╚{'═' * (w-2)}╝")

        if step.data_snapshot:
            print(f"\n{fmt_table(step.data_snapshot)}")

        print(f"\n{step.question}\n")
        print(f"  Варианты ответов:")
        for i, opt in enumerate(step.options, 1):
            print(f"    {i}. {opt.text}")

        while True:
            try:
                choice = input(f"\n  {'>'*5} Ваш выбор (1-{len(step.options)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(step.options):
                    break
                print(f"  Введите число от 1 до {len(step.options)}")
            except ValueError:
                print("  Введите число")

        chosen = step.options[idx]
        is_correct = chosen.is_correct

        results = list(session.state.get("step_results", []))
        results.append(is_correct)
        session.state["step_results"] = results

        health = session.state.get("health", 20)
        if is_correct:
            health = health + 20
            session.correct_answers += 1
        else:
            health = max(0, health - 30)
        session.state["health"] = health
        session.total_answers += 1

        icon = "✅" if is_correct else "❌"
        print(f"\n  {icon} {'ВЕРНО!' if is_correct else 'НЕВЕРНО'}")
        print(f"  {chosen.explanation}")
        print(f"{fmt_state(session.state)}")
        input(f"\n{'─' * w}\nНажми Enter, чтобы продолжить...")

    os.system("cls" if os.name == "nt" else "clear")
    print(fmt_title(f"🏁 {case.title} — ЗАВЕРШЁН"))

    pct = round((session.correct_answers / max(session.total_answers, 1)) * 100)
    wrong = session.total_answers - session.correct_answers
    health = session.state.get("health", 0)

    bar_len = 20
    filled = round(health / 100 * bar_len)
    bar = "█" * filled + "░" * (bar_len - filled)

    print(f"\n  ✅ Верно: {session.correct_answers}")
    print(f"  ❌ Неверно: {wrong}")
    print(f"  📊 Точность: {pct}%")
    print(f"  💊 Здоровье: [{bar}] {health:.0f}%\n")

    if pct >= 80 and health >= 70:
        print(f"  🏆 Отлично! Вы справились с кейсом!")
    elif pct >= 50:
        print(f"  👍 Неплохо, но есть куда расти.")
    else:
        print(f"  📖 Компания на грани. Попробуйте ещё раз.")

    print(f"\n{'─' * w}")


def main():
    w = shutil.get_terminal_size().columns

    cases = [build_case(AUDIT_CASES[i]) for i in range(len(AUDIT_CASES))]
    cases.append(build_case(DEMO_CASE))

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print(fmt_title("📊 ФИНАНСОВЫЙ ТРЕНАЖЁР"))
        print(f"\n  Выберите кейс:\n")
        for i, c in enumerate(cases, 1):
            diff = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(c.difficulty, "⚪")
            marker = "📘" if c.steps[0].options[0].text.find("ликвид") != -1 or any("кейс" in x for x in [c.title]) else "🎯"
            print(f"  {i}. {marker} {c.title}  {diff}")
        print(f"\n  0. Выход")

        try:
            choice = int(input(f"\n  {'>'*5} Ваш выбор: ").strip())
        except (ValueError, EOFError):
            break

        if choice == 0:
            print("\n  До свидания!")
            break
        if 1 <= choice <= len(cases):
            play_case(cases[choice - 1])
        else:
            print("  Неверный выбор")
            input("  Нажми Enter...")


if __name__ == "__main__":
    main()
