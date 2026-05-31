import sys
sys.path.insert(0, 'C:/Users/Dan/AppData/Local/Temp/opencode/finance_bot')
from audit_cases import AUDIT_CASES
from game_cases import GAME_CASES
import json, re

def analyze(name, cases):
    for case_idx, case in enumerate(cases):
        title = case.get("title", "")
        steps = case.get("steps", [])
        if not steps:
            steps_raw = case.get("steps_raw", [])
            if steps_raw:
                steps = steps_raw
        for step in steps:
            opts = step.get("options", [])
            lens = [len(o["text"]) for o in opts]
            if not lens:
                continue
            avg = sum(lens) / len(lens)
            max_l = max(lens)
            min_l = min(lens)
            spread = max_l - min_l
            if spread > 80:
                print(f"\n{name} Case {case_idx+1}: {title}")
                print(f"  Step {step.get('order')}: {step.get('title','')}")
                print(f"  Lengths: {lens}  avg={avg:.0f} spread={spread}")
                for o in opts:
                    flag = " LONG" if len(o["text"]) > avg * 1.4 else ("SHORT" if len(o["text"]) < avg * 0.6 else "     ")
                    print(f"    {flag} [{len(o['text']):3}] {o['text'][:100]}")

print("=== AUDIT CASES ===")
analyze("AUDIT", AUDIT_CASES)
print("\n=== GAME CASES ===")
analyze("GAME", GAME_CASES)
