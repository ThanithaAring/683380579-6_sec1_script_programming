# Week 11 (LabADV): Agentic Document Automator

A configuration-driven **Document Agent** that reads a list of tasks from a JSON file and runs them one by one: it fills a Word template, watermarks a PDF, merges PDFs, extracts text, and writes a JSON audit report of everything it did.

The sample content is based on the **Enhanced Task Manager** project (planning, design and sprint progress).

## Features

| Task type | What it does | Output |
|---|---|---|
| `generate_word_report` | Fills `{{PLACEHOLDERS}}` in a `.docx` template and inserts a table at `{{TABLE_PLACEHOLDER}}` | `documents/generated_report.docx` |
| `apply_pdf_watermark` | Stamps a rotated, semi-transparent text watermark on every page | `documents/watermarked_document.pdf` |
| `merge_pdfs` | Combines several PDFs into one | `documents/merged_docs.pdf` |
| `extract_word_text` | Saves the paragraph and table text of a `.docx` | `documents/extracted_word_text.txt` |
| `extract_pdf_text` | Saves the text of every PDF page | `documents/extracted_pdf_text.txt` |

Every run also writes `documents/reports/audit_report_<timestamp>.json`.

## Setup & How to Run

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python create_sample_files.py   # creates the Word template and the input PDFs
python main.py                  # runs all tasks in the config
```

To change what the agent does, edit `configs/document_automation_config.json` (report data, table rows, watermark text/colour/angle, which PDFs to merge). No code changes needed.

## Project Structure

```
agentic-document-automator/
├── configs/
│   └── document_automation_config.json   # tasks + data for the agent
├── src/
│   ├── __init__.py
│   ├── config_parser.py    # load + validate config, resolve paths
│   ├── document_agent.py   # runs tasks, writes audit report
│   ├── pdf_tasks.py        # watermark, merge, extract (PyPDF2 + reportlab)
│   ├── word_tasks.py       # template filling, table insert, extract (python-docx)
│   └── utils.py            # logging, directories, audit entries
├── templates/
│   └── report_template.docx
├── documents/              # inputs + generated outputs
├── screenshots/            # screenshots of the outputs
├── create_sample_files.py
├── main.py
├── requirements.txt
└── README.md
```

## Results

### merged_docs.pdf
![merged_docs.pdf](screenshots/merged_docs.png)

### generated_report.docx
![generated_report.docx](screenshots/generated_report.png)

### watermarked_document.pdf
![watermarked_document.pdf](screenshots/watermarked_document.png)

## Improvements over the starter example

* **Placeholders fully replaced** – the starter replaced `REPORT_TITLE` but left the braces, producing `{{Monthly Performance Summary}}`. Now `{{KEY}}` is replaced as a whole, even when Word splits it across several runs.
* **Table placed at `{{TABLE_PLACEHOLDER}}`** – the starter removed the placeholder but appended the table at the end of the document. Now the table is inserted exactly where the placeholder was.
* **Watermark matches each page size** and is built in memory (no temp file).
* **All paths resolved** – `output_path` was not converted to an absolute path, so the report was saved relative to wherever the script was launched.
* **Validation for every task type** and a clear list of missing input files.
* `src` is a real package (relative imports), and `requirements.txt` is filled in.
* `create_sample_files.py` generates all inputs, so the project runs from a fresh clone.
