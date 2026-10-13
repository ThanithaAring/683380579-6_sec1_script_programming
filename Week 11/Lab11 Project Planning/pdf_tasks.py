# agentic-document-automator/src/pdf_tasks.py
import io
import os

from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas

from .utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)


class PDFTasks:
    """PDF operations for the Document Agent: watermark, merge, extract text."""

    def __init__(self):
        logger.info("PDFTasks initialized.")

    def _create_watermark_page(self, text, page_width, page_height, font_size, color, angle):
        """Builds a one-page watermark PDF in memory, sized to match the target page."""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
        r, g, b, a = color
        c.setFillColor(Color(r, g, b, alpha=a))
        c.setFont('Helvetica-Bold', font_size)
        c.translate(page_width / 2, page_height / 2)
        c.rotate(angle)
        text_width = c.stringWidth(text, 'Helvetica-Bold', font_size)
        c.drawString(-text_width / 2, -font_size / 4, text)
        c.showPage()
        c.save()
        buffer.seek(0)
        return PdfReader(buffer).pages[0]

    def apply_watermark(self, input_pdf_path, output_pdf_path, watermark_text,
                        font_size=60, color=(0.5, 0.5, 0.5, 0.2), angle=45):
        if not os.path.exists(input_pdf_path):
            logger.error(f"Input PDF for watermarking not found: {input_pdf_path}")
            return False

        ensure_directory_exists(os.path.dirname(output_pdf_path))
        try:
            reader = PdfReader(input_pdf_path)
            writer = PdfWriter()
            for page in reader.pages:
                width = float(page.mediabox.width)
                height = float(page.mediabox.height)
                watermark = self._create_watermark_page(watermark_text, width, height, font_size, color, angle)
                page.merge_page(watermark)
                writer.add_page(page)
            with open(output_pdf_path, 'wb') as f:
                writer.write(f)
            logger.info(f"Watermark '{watermark_text}' applied to {len(reader.pages)} page(s) -> {output_pdf_path}")
            return True
        except Exception as e:
            logger.error(f"Error applying watermark to '{input_pdf_path}': {e}")
            return False

    def merge_pdfs(self, pdf_paths, output_path):
        if not pdf_paths:
            logger.warning("No PDFs given to merge.")
            return False

        writer = PdfWriter()
        ensure_directory_exists(os.path.dirname(output_path))
        for pdf_path in pdf_paths:
            if not os.path.exists(pdf_path):
                logger.warning(f"Skipping missing PDF: {pdf_path}")
                continue
            try:
                for page in PdfReader(pdf_path).pages:
                    writer.add_page(page)
                logger.info(f"Added '{os.path.basename(pdf_path)}' to merge.")
            except Exception as e:
                logger.error(f"Error reading PDF '{pdf_path}': {e}")

        if len(writer.pages) == 0:
            logger.error("Nothing to merge.")
            return False
        try:
            with open(output_path, 'wb') as f:
                writer.write(f)
            logger.info(f"Merged {len(writer.pages)} page(s) -> {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error writing merged PDF: {e}")
            return False

    def extract_text_from_pdf(self, pdf_path):
        if not os.path.exists(pdf_path):
            logger.error(f"PDF not found: {pdf_path}")
            return None
        try:
            reader = PdfReader(pdf_path)
            pages = [(page.extract_text() or "") + "\n--- Page End ---\n" for page in reader.pages]
            logger.info(f"Extracted text from {len(pages)} page(s) of {os.path.basename(pdf_path)}")
            return "".join(pages)
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return None
