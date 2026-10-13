# Agentic Data Processing (Advanced CSV & JSON Workflows)

A configuration-driven **DataAgent** that runs a multi-step CSV/JSON pipeline defined in
`configs/data_pipeline_config.json`. Data is passed between tasks through an internal
`data_store` using `input_data_key` / `output_data_key`.

## Pipeline
1. Load `data/input_sales.csv`
2. Aggregate sales by `Customer` (sum of `Amount`)
3. Save → `data/processed_sales_by_customer.csv`
4. Convert raw sales CSV → JSON
5. Save → `data/sales_data.json`
6. Load `data/input_inventory.json`
7. Update inventory (stock, layout, dpi, add PROD004, set color by product id)
8. Query `0.details.brand`
9. Save → `data/updated_inventory.json`
10. Write audit log → `reports/audit_report_*.json`

## How to Run
```bash
git clone https://github.com/<YOUR_USERNAME>/agentic-data-processor.git
cd agentic-data-processor
python main.py
```
Only the Python standard library is used (`csv`, `json`, `logging`). Python 3.8+.

## Project Structure
```
agentic-data-processor/
├── src/
│   ├── __init__.py
│   ├── data_agent.py        # orchestrator + data_store + task dispatcher
│   ├── csv_tasks.py         # load / save / aggregate / filter CSV
│   ├── json_tasks.py        # load / save / update / query JSON
│   ├── conversion_tasks.py  # CSV <-> JSON
│   ├── config_parser.py     # load + validate config
│   └── utils.py             # logging, directories, audit log
├── configs/data_pipeline_config.json
├── data/                    # inputs + generated outputs
├── main.py
├── .gitignore
└── README.md
```

## Fixes Made to the Lab Prototype
| Problem in original code | Fix |
|---|---|
| `main.py` imported modules directly from `src/` while modules use relative imports (`from .utils`) → `ImportError` | Import as a package: `from src.data_agent import DataAgent` |
| `ensure_directory_exists` used but not imported in `csv_tasks.py`, `json_tasks.py` | Added the import |
| `data_agent.py` used `sys` without importing it | Reports folder is now passed in from `main.py` |
| Config validator required `output_data_key` on `save_*` tasks → config rejected | `save_csv` / `save_json` no longer need it |
| `"path": ""` (add product to root list) was skipped | Empty path = root; `add_to_list` appends to the root list |
| `"PROD001.details.color"` could not navigate a list by text key | A text key on a list finds the item whose `id` matches |
| `csv_to_json` failed on values like `-5` | Uses `int()` / `float()` conversion with fallback |

## Results
- `processed_sales_by_customer.csv` – total Amount per customer
- `sales_data.json` – all sales rows with numeric types
- `updated_inventory.json` – 4 products with updated fields
