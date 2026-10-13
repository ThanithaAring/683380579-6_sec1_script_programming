# agentic-web-scraper/src/config_parser.py
"""Loads and validates the scraping configuration (the agent's "plan")."""

import json
import os


class ConfigParser:
    """Parses and validates the scraping configuration from a JSON file."""

    REQUIRED_FIELDS = ["start_url", "pagination_selector", "item_container_selector", "item_data_selectors"]
    REQUIRED_ITEM_FIELDS = ["name", "price"]

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        """Load the configuration from the JSON file and validate it."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in config file: {e}")

        self._validate_config()
        return self.config

    def _validate_config(self):
        """Make sure required fields exist and selectors have the right type."""
        for field in self.REQUIRED_FIELDS:
            if field not in self.config:
                raise ValueError(f"Missing required field in config: '{field}'")

        selectors = self.config["item_data_selectors"]
        for field in self.REQUIRED_ITEM_FIELDS:
            if not selectors.get(field):
                raise ValueError(f"Missing required item data selector: '{field}'")

        # A selector must be a string, or null (= this field does not exist on the page)
        for key, value in selectors.items():
            if value is not None and not isinstance(value, str):
                raise ValueError(f"Item data selector '{key}' must be a string or null.")

        if self.config["pagination_selector"] is not None and not isinstance(self.config["pagination_selector"], str):
            raise ValueError("Pagination selector must be a string or null.")
        if not isinstance(self.config["item_container_selector"], str):
            raise ValueError("Item container selector must be a string.")
