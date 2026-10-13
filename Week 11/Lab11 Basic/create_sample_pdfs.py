# document-automator/create_sample_pdfs.py
# Generates the sample input PDFs (input_article.pdf, dummy_doc1.pdf, dummy_doc2.pdf)
# Requires: pip install reportlab
import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documents')

PAGE_1 = [
    ("Introduction to Automation", True),
    ("", False),
    ("Automation is the creation and application of technology to produce and deliver", False),
    ("goods and services with minimal human intervention. The implementation of", False),
    ("automation technologies, techniques, and processes improves the efficiency,", False),
    ("reliability, and speed of many tasks that were previously performed manually.", False),
    ("", False),
    ("This leads to increased productivity, reduced costs, and improved quality.", False),
]

PAGE_2 = [
    ("Benefits of Automation", True),
    ("", False),
    ("1. Increased Efficiency: Tasks are completed faster and with higher throughput.", False),
    ("2. Cost Reduction: Lower labor costs and reduced waste.", False),
    ("3. Improved Accuracy: Minimizes human error.", False),
    ("4. Enhanced Safety: Dangerous tasks can be automated.", False),
    ("5. Greater Consistency: Uniform quality in output.", False),
    ("", False),
    ("Conclusion", True),
    ("", False),
    ("Automation is transforming industries globally. Embracing these technologies", False),
    ("is crucial for future competitiveness.", False),
]


def draw_page(c, lines):
    y = A4[1] - 72
    for text, is_heading in lines:
        c.setFont("Helvetica-Bold" if is_heading else "Helvetica", 16 if is_heading else 11)
        c.drawString(72, y, text)
        y -= 22 if is_heading else 16
    c.showPage()


def make_pdf(filename, pages):
    c = canvas.Canvas(os.path.join(DOCS_DIR, filename), pagesize=A4)
    for lines in pages:
        draw_page(c, lines)
    c.save()
    print(f"Created documents/{filename}")


if __name__ == "__main__":
    os.makedirs(DOCS_DIR, exist_ok=True)
    make_pdf("input_article.pdf", [PAGE_1, PAGE_2])
    make_pdf("dummy_doc1.pdf", [[("This is Dummy Document 1 for merging test.", False)]])
    make_pdf("dummy_doc2.pdf", [[("This is Dummy Document 2 for merging test.", False)]])
