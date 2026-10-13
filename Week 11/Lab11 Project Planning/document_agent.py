# agentic-document-automator/src/document_agent.py
import datetime
import json
import os

from .pdf_tasks import PDFTasks
from .utils import setup_logging, log_audit_entry, ensure_directory_exists
from .word_tasks import WordTasks

logger = setup_logging(__name__)


class DocumentAgent:
    """Runs every task in the config in order and writes a JSON audit report."""

    def __init__(self, config):
        self.config = config
        self.audit_log = []
        self.start_time = datetime.datetime.now()
        self.pdf = PDFTasks()
        self.word = WordTasks()
        self.handlers = {
            "generate_word_report": self._generate_word_report,
            "apply_pdf_watermark": self._apply_pdf_watermark,
            "merge_pdfs": self._merge_pdfs,
            "extract_pdf_text": self._extract_pdf_text,
            "extract_word_text": self._extract_word_text,
        }

    # ---- task handlers ----
    def _generate_word_report(self, task):
        placeholders = {**self.config.get("global_data", {}), **task.get("data", {})}
        return self.word.generate_report_from_template(
            task["template_path"], task["output_path"], placeholders, task.get("table_data"))

    def _apply_pdf_watermark(self, task):
        return self.pdf.apply_watermark(
            task["input_pdf"], task["output_pdf"], task["watermark_text"],
            task.get("font_size", 60), tuple(task.get("color", [0.5, 0.5, 0.5, 0.2])), task.get("angle", 45))

    def _merge_pdfs(self, task):
        return self.pdf.merge_pdfs(task["input_pdfs"], task["output_pdf"])

    def _extract_pdf_text(self, task):
        return self._save_text(self.pdf.extract_text_from_pdf(task["input_pdf"]), task["output_text_file"])

    def _extract_word_text(self, task):
        return self._save_text(self.word.extract_text_from_word(task["input_docx"]), task["output_text_file"])

    @staticmethod
    def _save_text(text, path):
        if not text:
            return False
        ensure_directory_exists(os.path.dirname(path))
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        return True

    # ---- runner ----
    def _process_task(self, task):
        task_type = task.get("type")
        name = task.get("name", task_type)
        log_audit_entry(self.audit_log, "INFO", f"Starting task '{name}'", task_type)
        try:
            ok = self.handlers[task_type](task)
            status = "SUCCESS" if ok else "ERROR"
            log_audit_entry(self.audit_log, status, f"Task '{name}' {'completed' if ok else 'failed'}.", task_type)
            return ok
        except Exception as e:
            log_audit_entry(self.audit_log, "ERROR", f"Error in '{name}': {e}", task_type)
            return False

    def _write_audit_report(self, output_dir):
        ensure_directory_exists(output_dir)
        path = os.path.join(output_dir, f"audit_report_{datetime.datetime.now():%Y%m%d_%H%M%S}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_log, f, indent=4, ensure_ascii=False)
        logger.info(f"Audit report saved -> {path}")

    def run(self):
        log_audit_entry(self.audit_log, "INFO", "Document Agent started.", "agent_run")
        results = [self._process_task(task) for task in self.config["tasks"]]
        duration = (datetime.datetime.now() - self.start_time).total_seconds()
        log_audit_entry(self.audit_log, "INFO",
                        f"Finished {sum(results)}/{len(results)} tasks successfully in {duration:.2f}s.",
                        "agent_run_summary")
        report_dir = os.path.join(os.path.dirname(self.config['output_files']['generated_report']), 'reports')
        self._write_audit_report(report_dir)
        return all(results)
