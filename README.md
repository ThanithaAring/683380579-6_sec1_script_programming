# Automating with CSV and JSON Data

Python script that reads, processes and writes CSV and JSON files using the built-in `csv` and `json` modules.

## What it does
**CSV**
- Reads `data/input_sales.csv` with `csv.DictReader`
- Calculates total sales and average price
- Keeps only sales with Amount >= 100
- Writes the result + a SUMMARY row to `data/output_filtered_sales.csv`

**JSON**
- Reads `data/input_inventory.json`
- Updates stock: PROD001 → 60, PROD003 → 75
- Adds a new product PROD004 (Gaming Headset)
- Writes the result to `data/output_updated_inventory.json`

## How to Run
```bash
python main.py
```
No extra packages needed (Python 3.8+).

## Project Structure
```
data-processor/
├── src/
│   ├── __init__.py
│   ├── csv_handler.py
│   ├── json_handler.py
│   └── utils.py
├── data/
│   ├── input_sales.csv
│   ├── input_inventory.json
│   ├── output_filtered_sales.csv
│   └── output_updated_inventory.json
├── screenshots/
├── main.py
├── .gitignore
└── README.md
```

## Screenshots

### output_filtered_sales.csv
![output_filtered_sales.csv](screenshots/output_filtered_sales.png)

### output_updated_inventory.json
![output_updated_inventory.json](screenshots/output_updated_inventory.png)
