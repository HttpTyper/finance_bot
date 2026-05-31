import sys, re
sys.path.insert(0, 'C:/Users/Dan/AppData/Local/Temp/opencode/finance_bot')
from audit_cases import AUDIT_CASES
from game_cases import GAME_CASES

def find_english(text, context=""):
    # Find words that contain Latin letters (but skip common abbreviations/units)
    words = re.findall(r'\b[A-Za-z]{2,}\b', text)
    # Filter out common abbreviations and measurement units
    skip = {'llc', 'ooo', 'npv', 'irr', 'ebit', 'wacc', 'ros', 'roa', 'roe', 'icr',
            'dsr', 'dso', 'dpo', 'sofr', 'euribor', 'irs', 'jit', 'pi', 'kpi',
            'mca', 'nsc', 'cfo', 'ceo', 'cagr', 'eps', 'ebitda',
            'srt', 'ms', 'km', 'tn', 'kol', 'tys', 'rub', 'usd', 'eur'}
    found = []
    for w in words:
        if w.lower() not in skip:
            found.append(w)
    return found

def scan(name, cases):
    for ci, case in enumerate(cases):
        title = case.get("title", "")
        for step in case.get("steps", []):
            opts = step.get("options", [])
            for oi, opt in enumerate(opts):
                eng = find_english(opt["text"])
                if eng:
                    print(f'{name} c{ci+1} s{step["order"]} o{oi+1}: {eng} -> {opt["text"][:80]}')

scan("AUDIT", AUDIT_CASES)
scan("GAME", GAME_CASES)
