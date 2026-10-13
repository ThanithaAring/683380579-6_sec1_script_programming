# agentic-document-automator/main.py
import os
import sys

from src.config_parser import ConfigParser
from src.document_agent import DocumentAgent
from src.utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def missing_input_files(config):
    """Returns the list of input files the tasks need but that don't exist yet."""
    needed = []
    for task in config['tasks']:
        if task['type'] == 'generate_word_report':
            needed.append(task['template_path'])
        elif task['type'] in ('apply_pdf_watermark', 'extract_pdf_text'):
            needed.append(task['input_pdf'])
        elif task['type'] == 'merge_pdfs':
            needed.extend(task['input_pdfs'])
    return [p for p in needed if not os.path.exists(p)]


def main():
    ensure_directory_exists(os.path.join(BASE_DIR, 'documents'))
    ensure_directory_exists(os.path.join(BASE_DIR, 'templates'))

    config = ConfigParser(os.path.join(BASE_DIR, 'configs', 'document_automation_config.json')).load_config()
    config = ConfigParser.resolve_paths(config, BASE_DIR)

    missing = missing_input_files(config)
    if missing:
        for path in missing:
            logger.critical(f"Missing input file: {os.path.relpath(path, BASE_DIR)}")
        logger.info("Run 'python create_sample_files.py' first.")
        sys.exit(1)

    ok = DocumentAgent(config).run()
    logger.info("Document automation process completed." if ok else "Finished with errors - see audit report.")


if __name__ == "__main__":
    main()
