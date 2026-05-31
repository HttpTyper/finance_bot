import sys
sys.path.insert(0, 'C:/Users/Dan/AppData/Local/Temp/opencode/finance_bot')
from services.engine import format_table

from audit_cases import AUDIT_CASES

# Test case 2 - Рентабельность
case = AUDIT_CASES[1]
for step in case["steps"]:
    ds = step.get("data_snapshot")
    if ds:
        tbl = ds["tables"][0]
        headers = tbl["headers"]
        rows = tbl["rows"]
        print(f"Table: {tbl['title']}")
        print(f"Headers: {headers}")
        
        # Calculate col_widths the same way as format_table
        col_widths = [
            max(
                max((len(str(row[i])) if i < len(row) else 0) for row in rows),
                len(h),
            ) + 2
            for i, h in enumerate(headers)
        ]
        print(f"col_widths: {col_widths}")
        
        top = "┌" + "┬".join("─" * w for w in col_widths) + "┐"
        print(f"top line: {top}")
        print(f"top len: {len(top)}")
        
        # Count dashes per column
        for i, w in enumerate(col_widths):
            print(f"  col {i}: width={w}, dashes={'─' * w}, count={len('─' * w)}")
        
        print()
        
        # Also check what format_table produces
        rendered = format_table(ds)
        first_line = rendered.split('\n')[0]
        print(f"format_table first line: {first_line}")
        print(f"format_table first line len: {len(first_line)}")
        break
