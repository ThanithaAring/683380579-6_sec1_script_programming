# agentic-document-automator/src/utils.py
import datetime
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_logging(name, level=logging.INFO, filename=None):
    """Returns a logger with a console handler (and an optional file handler)."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        if filename:
            fh = logging.FileHandler(filename, encoding='utf-8')
            fh.setFormatter(formatter)
            logger.addHandler(fh)
    return logger


def ensure_directory_exists(path):
    """Creates a directory if it does not exist."""
    if not path:
        return
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        logging.error(f"Error creating directory {path}: {e}")
        raise


def log_audit_entry(audit_log_list, status, message, task_type="N/A", details=None):
    """Appends a structured entry to the audit log and echoes it to the console."""
    entry = {
        "timestamp": datetime.datetime.now().isoformat(timespec='seconds'),
        "status": status,
        "task_type": task_type,
        "message": message,
        "details": details or {},
    }
    audit_log_list.append(entry)
    if status in ("ERROR", "CRITICAL"):
        logging.error(f"AUDIT - {status}: {message} | Task: {task_type}")
    else:
        logging.info(f"AUDIT - {status}: {message} | Task: {task_type}")
