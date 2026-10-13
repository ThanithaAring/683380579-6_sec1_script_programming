# agentic-data-processor/src/json_tasks.py
import copy
import json
import os
from .utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)


class JSONTasks:
    """Handles reading, writing, and manipulation of JSON data."""

    def __init__(self):
        logger.info("JSONTasks initialized.")

    def load_json(self, file_path):
        """Loads a JSON file and returns the Python object."""
        if not os.path.exists(file_path):
            logger.error(f"JSON file not found: {file_path}")
            return None
        try:
            with open(file_path, mode='r', encoding='utf-8') as file:
                data = json.load(file)
            logger.info(f"Successfully loaded JSON from '{file_path}'.")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in '{file_path}': {e}")
            return None

    def save_json(self, data, file_path, indent=2):
        """Saves a Python object to a JSON file, pretty-printed."""
        ensure_directory_exists(os.path.dirname(file_path))
        try:
            with open(file_path, mode='w', encoding='utf-8') as file:
                json.dump(data, file, indent=indent, ensure_ascii=False)
            logger.info(f"Successfully saved JSON to '{file_path}'.")
            return True
        except Exception as e:
            logger.error(f"Error saving JSON file '{file_path}': {e}")
            return False

    # ---------- path helpers ----------
    @staticmethod
    def _step(node, key):
        """
        Moves one level down the JSON tree.
        - dict  -> node[key]
        - list + numeric key -> node[int(key)]
        - list + text key    -> the item whose "id" equals key (e.g. "PROD001")
        Returns (found, child).
        """
        if isinstance(node, dict):
            return (key in node), node.get(key)
        if isinstance(node, list):
            if key.isdigit():
                idx = int(key)
                return (0 <= idx < len(node)), (node[idx] if 0 <= idx < len(node) else None)
            for item in node:
                if isinstance(item, dict) and item.get("id") == key:
                    return True, item
        return False, None

    def update_json_data(self, data, updates):
        """
        Applies a list of updates: {"path": "a.b.c", "value": ..., "operation": "set|add_to_list|remove_from_list"}
        An empty path "" means the root object (e.g. append a new item to the root list).
        """
        if not data:
            logger.warning("No JSON data provided for update.")
            return data

        modified = copy.deepcopy(data)  # don't modify the original

        for update in updates or []:
            path = update.get("path")
            value = update.get("value")
            operation = update.get("operation", "set")

            if path is None:
                logger.warning(f"Update skipped: missing 'path': {update}")
                continue

            # ----- root-level operations (path == "") -----
            if path == "":
                if operation == "add_to_list" and isinstance(modified, list):
                    modified.append(value)
                    logger.info(f"Added new item to root list: {value.get('id', value) if isinstance(value, dict) else value}")
                elif operation == "remove_from_list" and isinstance(modified, list) and value in modified:
                    modified.remove(value)
                    logger.info("Removed item from root list.")
                else:
                    logger.warning(f"Cannot apply '{operation}' to root. Skipping: {update}")
                continue

            keys = path.split('.')
            parent = modified
            ok = True
            for key in keys[:-1]:
                ok, parent = self._step(parent, key)
                if not ok:
                    logger.warning(f"Path '{path}' not found at key '{key}'. Skipping update.")
                    break
            if not ok:
                continue

            target = keys[-1]
            try:
                if operation == "set":
                    if isinstance(parent, dict):
                        parent[target] = value
                    elif isinstance(parent, list) and target.isdigit() and int(target) < len(parent):
                        parent[int(target)] = value
                    else:
                        logger.warning(f"Cannot 'set' at '{path}'. Skipping.")
                        continue
                    logger.info(f"Set '{path}' to '{value}'.")
                elif operation in ("add_to_list", "remove_from_list"):
                    found, lst = self._step(parent, target)
                    if not found or not isinstance(lst, list):
                        logger.warning(f"Target at '{path}' is not a list. Skipping.")
                        continue
                    if operation == "add_to_list":
                        lst.append(value)
                        logger.info(f"Added '{value}' to list at '{path}'.")
                    elif value in lst:
                        lst.remove(value)
                        logger.info(f"Removed '{value}' from list at '{path}'.")
                    else:
                        logger.warning(f"Value '{value}' not in list at '{path}'.")
                else:
                    logger.warning(f"Unsupported operation '{operation}'. Skipping.")
            except Exception as e:
                logger.error(f"Error applying JSON update for path '{path}': {e}")

        return modified

    def query_json_data(self, data, path):
        """Returns the value at a dot-notation path, or None if not found."""
        if not data:
            logger.warning("No JSON data to query.")
            return None
        node = data
        for key in path.split('.'):
            found, node = self._step(node, key)
            if not found:
                logger.warning(f"Query path '{path}' failed at key '{key}'.")
                return None
        logger.info(f"Successfully queried '{path}'. Result: {node}")
        return node
