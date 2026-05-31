import sys, re
sys.path.insert(0, 'C:/Users/Dan/AppData/Local/Temp/opencode/finance_bot')
from audit_cases import AUDIT_CASES
from game_cases import GAME_CASES

# Find options with extreme spreads
def find_extreme(cases, name):
    issues = []
    for ci, case in enumerate(cases):
        for step in case.get("steps", []):
            opts = step.get("options", [])
            lens = [len(o["text"]) for o in opts]
            if not lens:
                continue
            avg = sum(lens) / len(lens)
            max_l = max(lens)
            min_l = min(lens)
            correct_text = ""
            correct_len = 0
            for o in opts:
                if o["is_correct"]:
                    correct_text = o["text"]
                    correct_len = len(o["text"])
                    break
            issues.append({
                "case": ci,
                "step": step["order"],
                "title": step.get("title",""),
                "lens": lens,
                "avg": avg,
                "max": max_l,
                "min": min_l,
                "spread": max_l - min_l,
                "correct_len": correct_len,
            })
    return issues

issues = find_extreme(AUDIT_CASES, "AUDIT")
sorted_issues = sorted(issues, key=lambda x: -x["spread"])
print(f"{'spread':>6} {'correct':>8} {'avg':>6} {'case':>4} step {'title'}")
print("-" * 70)
for i in sorted_issues[:25]:
    print(f"{i['spread']:>6} {i['correct_len']:>8} {i['avg']:>6.0f} {i['case']+1:>4} {i['step']} {i['title'][:40]}")
