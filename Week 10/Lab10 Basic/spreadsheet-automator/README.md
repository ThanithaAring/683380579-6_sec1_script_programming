# Automating Spreadsheets (Excel)

Python script that reads sales data from an Excel file, calculates totals, and writes a formatted report to a new Excel file using `openpyxl`.

## What it does
1. Loads `data/input_sales.xlsx` (Product Name, Quantity, Unit Price)
2. Calculates Total Price for each item (Quantity × Unit Price)
3. Calculates the Grand Total
4. Writes a formatted report to `data/output_sales_report.xlsx`
   - Green bold header
   - Borders and number format `#,##0.00`
   - Yellow Grand Total row
   - Auto column width
5. Skips empty rows automatically

## How to Run
```bash
pip install openpyxl
python main.py
```

## Project Structure
```
spreadsheet-automator/
├── src/
│   ├── __init__.py
│   └── excel_processor.py
├── data/
│   ├── input_sales.xlsx
│   └── output_sales_report.xlsx
├── screenshots/
│   └── output_sales_report.png
├── main.py
├── .gitignore
└── README.md
```

## Result

| Product Name | Quantity | Unit Price | Total Price |
|---|---|---|---|
| Laptop | 2 | 1200.5 | 2,401.00 |
| Mouse | 5 | 25 | 125.00 |
| Keyboard | 3 | 75.99 | 227.97 |
| Monitor | 1 | 300 | 300.00 |
| Printer | 1 | 150 | 150.00 |
| **Grand Total:** | | | **3,203.97** |

## Screenshot

![output_sales_report.xlsx](screenshots/output_sales_report.png)
