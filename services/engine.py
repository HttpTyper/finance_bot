import re

from database.models import Step, Option, Session, Case


INITIAL_STATE = {
    "cash": 0,
    "receivables": 0,
    "inventory": 0,
    "payables": 0,
    "loan": 0,
    "equity": 0,
    "revenue": 0,
    "profit": 0,
    "total_assets": 0,
    "total_liabilities": 0,
    "health": 20,
    "step_results": [],
}


def apply_effects(state: dict, effects: dict) -> dict:
    new_state = dict(state)
    for key, value in (effects or {}).items():
        new_state[key] = new_state.get(key, 0) + value
    return new_state


def _is_numeric(val) -> bool:
    s = str(val).strip()
    if not s:
        return False
    return bool(re.fullmatch(r"[\(\[\-]?[\d\s,.]+[\)\]%]?", s))


def _col_align(col_index: int, rows: list, headers: list) -> str:
    if col_index == 0 and len(headers) > 1:
        return "ljust"
    values = [str(r[col_index]) for r in rows if col_index < len(r) and str(r[col_index]).strip()]
    if not values:
        return "center"
    numeric_count = sum(1 for v in values if _is_numeric(v))
    return "rjust" if numeric_count > len(values) / 2 else "ljust"


def format_table(data: dict) -> str:
    if not data or "tables" not in data:
        return ""
    lines = []
    for table in data["tables"]:
        title = table.get("title", "")
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        lines.append(f"📊 <b>{title}</b>")
        if not headers and not rows:
            lines.append("")
            continue
        if headers:
            col_widths = [
                max(
                    max((len(str(row[i])) if i < len(row) else 0) for row in rows),
                    len(h),
                ) + 2
                for i, h in enumerate(headers)
            ]
            sep = "├" + "┼".join("─" * w for w in col_widths) + "┤"
            bot = "└" + "┴".join("─" * w for w in col_widths) + "┘"
            hdr = "│" + "│".join(f" {h.center(col_widths[i] - 2)} " for i, h in enumerate(headers)) + "│"
            lines.append(f"<pre>{hdr}\n{sep}")
            aligns = [_col_align(i, rows, headers) for i in range(len(headers))]
            for row in rows:
                cells = []
                for i in range(len(headers)):
                    if i < len(row):
                        val = str(row[i])
                        w = col_widths[i] - 2
                        if aligns[i] == "ljust":
                            formatted = val.ljust(w)
                        elif aligns[i] == "rjust":
                            formatted = val.rjust(w)
                        else:
                            formatted = val.center(w)
                        cells.append(f" {formatted} ")
                    else:
                        cells.append(" " * col_widths[i])
                rline = "│" + "│".join(cells) + "│"
                lines.append(rline)
            lines.append(bot + "</pre>")
        else:
            for row in rows:
                label = str(row[0]) if row else ""
                values = [str(v) for v in row[1:]]
                if values:
                    lines.append(f"  {label} — {' | '.join(values)}")
                else:
                    lines.append(f"  {label}")
        lines.append("")
    return "\n".join(lines)


def health_bar(health: int) -> str:
    filled = max(0, min(10, health // 10))
    empty = 10 - filled
    bar = "█" * filled + "░" * empty
    return f"💊 Здоровье: <b>{bar} {health}%</b>"


def format_state_summary(state: dict) -> str:
    lines = [
        f"🏢 <b>Текущее состояние компании</b>\n",
        f"• Денежные средства: <b>{state.get('cash', 0):,}</b>",
        f"• Дебиторка: <b>{state.get('receivables', 0):,}</b>",
        f"• Запасы: <b>{state.get('inventory', 0):,}</b>",
        f"• Кредиторка: <b>{state.get('payables', 0):,}</b>",
        f"• Кредиты: <b>{state.get('loan', 0):,}</b>",
        f"• Выручка: <b>{state.get('revenue', 0):,}</b>",
        f"• Прибыль: <b>{state.get('profit', 0):,}</b>",
        f"• Активы: <b>{state.get('total_assets', 0):,}</b>",
        f"\n{health_bar(state.get('health', 0))}",
    ]
    return "\n".join(lines)


class GameEngine:
    def __init__(self, case: Case, session: Session):
        self.case = case
        self.session = session
        self.steps: list[Step] = sorted(case.steps, key=lambda s: s.order)

    @property
    def total_steps(self) -> int:
        return len(self.steps)

    @property
    def is_finished(self) -> bool:
        return self.session.current_step >= self.total_steps

    def get_current_step(self) -> Step | None:
        if self.is_finished or self.total_steps == 0:
            return None
        return self.steps[self.session.current_step]

    def get_step_data_text(self, step: Step) -> str:
        return format_table(step.data_snapshot) if step.data_snapshot else ""

    def get_question_text(self, step: Step) -> str:
        parts = []
        if step.title:
            parts.append(f"<b>{step.title}</b>")
        parts.append(step.question)
        return "\n\n".join(parts)

    def check_answer(self, option: Option) -> bool:
        return option.is_correct

    def apply_answer(self, option: Option):
        if option.effects:
            self.session.state = apply_effects(self.session.state, option.effects)
        is_correct = option.is_correct
        results = list(self.session.state.get("step_results", []))
        results.append(is_correct)
        self.session.state["step_results"] = results
        health = self.session.state.get("health", 20)
        if is_correct:
            health = health + 20
        else:
            health = max(0, health - 30)
        self.session.state["health"] = health
        self.session.current_step += 1
        if is_correct:
            self.session.correct_answers += 1
        self.session.total_answers += 1

    def get_progress_text(self) -> str:
        total = self.total_steps
        results = self.session.state.get("step_results", [])
        parts = []
        for i in range(total):
            if i < len(results):
                parts.append("🟢" if results[i] else "🔴")
            else:
                parts.append("⚪")
        bar = "".join(parts)
        done = len(results)
        return f"Прогресс: {bar} ({done}/{total})"

    def get_result_text(self) -> str:
        health = self.session.state.get("health", 0)
        pct = round((self.session.correct_answers / max(self.session.total_answers, 1)) * 100)
        wrong_count = self.session.total_answers - self.session.correct_answers
        lines = [
            "🎯 <b>Симуляция завершена!</b>\n",
            f"✅ Верно: {self.session.correct_answers}",
            f"❌ Неверно: {wrong_count}",
            f"\n{health_bar(health)}\n",
            "─" * 20,
        ]
        if pct >= 80 and health >= 70:
            lines.append("🏆 Отличный результат! Вы спасли компанию!")
        elif pct >= 50:
            lines.append("👍 Неплохо, но есть куда расти. Изучите пояснения.")
        else:
            lines.append("📖 Компания на грани банкротства. Попробуйте ещё раз.")
        lines.append(format_state_summary(self.session.state))
        return "\n".join(lines)
