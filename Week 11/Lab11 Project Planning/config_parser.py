# agentic-document-automator/src/config_parser.py
import json
import os

from .utils import setup_logging

logger = setup_logging(__name__)

# Required keys for each task type
REQUIRED_TASK_FIELDS = {
    "generate_word_report": ["template_path", "output_path"],
    "apply_pdf_watermark": ["input_pdf", "output_pdf", "watermark_text"],
    "merge_pdfs": ["input_pdfs", "output_pdf"],
    "extract_pdf_text": ["input_pdf", "output_text_file"],
    "extract_word_text": ["input_docx", "output_text_file"],
}

# Keys that hold file paths (resolved to absolute paths later)
PATH_KEYS = ["template_path", "output_path", "input_pdf", "output_pdf", "input_docx", "output_text_file"]


class ConfigParser:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        if not os.path.exists(self.config_path):
            logger.critical(f"Configuration file not found: {self.config_path}")
            raise FileNotFoundError(self.config_path)
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            logger.critical(f"Invalid JSON in config file: {e}")
            raise ValueError(f"Invalid JSON in config file: {e}")
        self._validate_config()
        logger.info(f"Configuration loaded from {self.config_path}")
        return self.config

    def _validate_config(self):
        for field in ("global_data", "output_files", "tasks"):
            if field not in self.config:
                raise ValueError(f"Missing required field in config: '{field}'")
        if not isinstance(self.config["tasks"], list):
            raise ValueError("Config field 'tasks' must be a list.")

        for i, task in enumerate(self.config["tasks"]):
            task_type = task.get("type")
            if task_type not in REQUIRED_TASK_FIELDS:
                raise ValueError(f"Task {i} has unknown or missing 'type': {task_type}")
            missing = [k for k in REQUIRED_TASK_FIELDS[task_type] if k not in task]
            if missing:
                raise ValueError(f"Task {i} ('{task_type}') is missing: {', '.join(missing)}")
        logger.info("Configuration validated.")

    @staticmethod
    def resolve_paths(config, base_dir):
        """Turns every relative path in the config into an absolute path under base_dir."""
        config['output_files'] = {k: os.path.join(base_dir, v) for k, v in config['output_files'].items()}
        for task in config['tasks']:
            for key in PATH_KEYS:
                if key in task:
                    task[key] = os.path.join(base_dir, task[key])
            if 'input_pdfs' in task:
                task['input_pdfs'] = [os.path.join(base_dir, p) for p in task['input_pdfs']]
        return config
