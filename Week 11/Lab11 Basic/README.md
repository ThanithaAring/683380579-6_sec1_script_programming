# Week 11: Automating PDFs & Word Documents

This project automates common PDF and Word tasks with Python, using `PyPDF2` for PDF manipulation and `python-docx` for Word document generation.

## Key Concepts Demonstrated

* **PDF Text Extraction**: reading text content from PDF files.
* **PDF Merging**: combining multiple PDF files into one document.
* **Word Document Creation**: generating `.docx` files programmatically.
* **Adding Content to Word**: headings, paragraphs, formatted text (bold, italic, font size, alignment) and tables.
* **Modular Design**: PDF and Word logic in separate modules (`pdf_processor.py`, `word_processor.py`).
* **Robustness**: error handling and logging for each step.

## Setup & How to Run

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python create_sample_pdfs.py    # creates input_article.pdf, dummy_doc1.pdf, dummy_doc2.pdf
python main.py                  # creates output_report.docx and merged_output.pdf
```

The script will:
* Extract text from `documents/input_article.pdf`.
* Create `documents/output_report.docx` with a heading, formatted text, the extracted content and a summary table.
* Merge `dummy_doc1.pdf` and `dummy_doc2.pdf` into `documents/merged_output.pdf`.

## Project Structure

```
document-automator/
├── src/
│   ├── __init__.py
│   ├── pdf_processor.py     # PyPDF2: extract, merge, split
│   ├── word_processor.py    # python-docx: create, add content, format, tables
│   └── utils.py             # logging, directory helpers
├── documents/
│   ├── input_article.pdf    # sample input (from create_sample_pdfs.py)
│   ├── dummy_doc1.pdf       # sample input for merging
│   ├── dummy_doc2.pdf       # sample input for merging
│   ├── output_report.docx   # generated Word report
│   └── merged_output.pdf    # generated merged PDF
├── screenshots/
│   ├── merged_output.png
│   └── output_report.png
├── create_sample_pdfs.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Results

### merged_output.pdf
![merged_output.pdf](screenshots/merged_output.png)

### output_report.docx
![output_report.docx](screenshots/output_report.png)

## Fixes Applied to the Lab Starter Code

* `range(0_int, ...)` → `range(0, ...)` (syntax error in `split_pdf`).
* Imported the missing `ensure_directory_exists` in `pdf_processor.py`.
* `main.py` now imports `src.*` as a package so the relative imports inside `src/` work.
* `datetime` is imported at the top of `main.py`.
* Table column widths are set per cell, so Word actually applies them.
* `.gitignore` no longer uses inline comments (Git doesn't support them).
