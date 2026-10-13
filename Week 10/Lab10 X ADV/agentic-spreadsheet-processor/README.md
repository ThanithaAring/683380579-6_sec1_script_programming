# Advanced Spreadsheet Automation & Agentic Workflows

A config-driven **Spreadsheet Agent** built with `openpyxl`. The agent reads a list of tasks from
`configs/example_spreadsheet_config.json` and executes them one by one on `data/input_data.xlsx`,
then saves the result to `data/output_report.xlsx`.

## Tasks performed by the agent
| # | Task type | What it does |
|---|---|---|
| 1 | `copy_data` | Copy sheet **SalesData** → **Raw Data** |
| 2 | `calculate_column` | Column D = `Total Revenue` (`=B*C`) |
| 3 | `conditional_format` | 3-color scale (red → yellow → green) on Total Revenue |
| 4 | `chart` | Bar chart "Top 4 Product Revenue" |
| 5 | `calculate_column` | Column E = `Status` (`High Value` if revenue > 1000) |
| 6 | `conditional_format` | Highlight "High Value" rows in green |
| – | Audit Log | Sheet **Audit Log** records every step |

## How to Run
```bash
pip install openpyxl
python main.py
```

## Output workbook sheets
- **Audit Log** – timestamp, status, task type and message for every step
- **SalesData** – original input data
- **Raw Data** – copied data + Total Revenue + Status + conditional formatting + bar chart

## Project Structure
```
agentic-spreadsheet-processor/
├── src/
│   ├── __init__.py
│   ├── spreadsheet_agent.py
│   ├── config_parser.py
│   ├── utils.py
│   └── google_sheets_utils.py
├── configs/
│   └── example_spreadsheet_config.json
├── data/
│   ├── input_data.xlsx
│   └── output_report.xlsx
├── screenshots/
├── main.py
├── .gitignore
└── README.md
```

## Fixes made to the lab prototype
| Problem in original code | Fix |
|---|---|
| `main.py` used `from .src.utils import ...` → `ImportError` | Import as a package: `from src.utils import ...` |
| `spreadsheet_agent.py` used `json.dumps` without `import json` | Added the import |
| Config validator required `sheet` on every task, but `copy_data` has none → config rejected | `copy_data` is validated by `source_sheet` / `dest_sheet` |
| `conditional_formatting.add(range, ruleType=...)` is not valid openpyxl syntax | Build a `Rule(type='expression', ...)` object |
| Paths depended on the folder you run from | Paths are now relative to `main.py` |

## Screenshots

### Audit Log
![Audit Log](screenshots/audit_log.png)

### SalesData
![SalesData](screenshots/sales_data.png)

### Raw Data
![Raw Data](screenshots/raw_data.png)
