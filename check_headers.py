import sys, json
sys.path.insert(0, 'C:/Users/Dan/AppData/Local/Temp/opencode/finance_bot')
from audit_cases import AUDIT_CASES

for idx in [6, 7, 8, 9, 10, 11, 12, 13, 14]:  # 0-indexed = cases 7-15
    case = AUDIT_CASES[idx]
    print(f"CASE {idx+1}: {case.get('title','')}")
    print(f"  theory length: {len(case.get('theory',''))}")
    print(f"  steps count: {len(case.get('steps',[]))}")
    for s in case.get("steps", []):
        has_ds = "YES" if s.get("data_snapshot") else "NO"
        print(f"  Step {s.get('order')}: {s.get('title','')}  data_snapshot: {has_ds}")
    print()
