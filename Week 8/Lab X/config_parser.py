# agentic-data-processor/src/config_parser.py
import json
import os
from .utils import setup_logging

logger = setup_logging(__name__)


class ConfigParser:
    """Parses and validates the data automation configuration from a JSON file."""

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        """Loads the configuration from the specified JSON file."""
        if not os.path.exists(self.config_path):
            logger.critical(f"Configuration file not found: {self.config_path}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            logger.critical(f"Invalid JSON format in config file: {e}")
            raise ValueError(f"Invalid JSON format in config file: {e}")
        self._validate_config()
        logger.info(f"Configuration loaded successfully from {self.config_path}")
        return self.config

    def _validate_config(self):
        """Validates required fields and task structures."""
        if "tasks" not in self.config:
            raise ValueError("Missing required field in config: 'tasks'")
        if not isinstance(self.config["tasks"], list):
            raise ValueError("Config field 'tasks' must be a list.")

        # Save tasks write to files, so they don't need an output_data_key
        no_output_key_types = ["save_csv", "save_json"]
        needs_input_types = ["save_csv", "save_json", "transform_csv_aggregate", "filter_csv",
                             "update_json_data", "query_json_data",
                             "csv_to_json_conversion", "json_to_csv_conversion"]

        for i, task in enumerate(self.config["tasks"]):
            if "type" not in task:
                raise ValueError(f"Task {i} is missing 'type' field.")
            t = task["type"]
            if t not in no_output_key_types and "output_data_key" not in task:
                raise ValueError(f"Task {i} (type: {t}) is missing 'output_data_key' field.")
            if t in ["load_csv", "load_json", "save_csv", "save_json"] and "file_path" not in task:
                raise ValueError(f"Task {i} (type: {t}) requires 'file_path'.")
            if t in needs_input_types and "input_data_key" not in task:
                raise ValueError(f"Task {i} (type: {t}) requires 'input_data_key'.")
            if t == "save_csv" and "fieldnames" not in task:
                logger.warning(f"Task {i} (save_csv) has no explicit 'fieldnames'. Will derive from data.")

        logger.info("Configuration validated.")
