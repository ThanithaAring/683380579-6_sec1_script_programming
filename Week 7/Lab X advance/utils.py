# agentic-web-scraper/src/utils.py
"""Helper functions: saving data, explicit waits and robust clicking."""

import csv
import json
import os
import time

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def save_data_to_json(data, filename, directory="data"):
    """Save a list of dictionaries to a JSON file. Returns the file path or None."""
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return filepath
    except IOError as e:
        print(f"Error saving data to JSON file: {e}")
        return None


def save_data_to_csv(data, filename, directory="data"):
    """Save a list of dictionaries to a CSV file. Returns the file path or None."""
    if not data:
        return None
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    try:
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return filepath
    except IOError as e:
        print(f"Error saving data to CSV file: {e}")
        return None


def wait_for_element(driver, by, value, timeout=10):
    """Explicit wait: return the element once it is visible, or None on timeout."""
    try:
        return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))
    except TimeoutException:
        return None


def robust_click(driver, by, value, max_attempts=3, delay_between_attempts=2):
    """Retry mechanism: try to click an element several times before giving up."""
    for attempt in range(1, max_attempts + 1):
        try:
            element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((by, value)))
            element.click()
            return True
        except (TimeoutException, WebDriverException) as e:
            print(f"Click attempt {attempt} failed: {type(e).__name__}")
            if attempt < max_attempts:
                time.sleep(delay_between_attempts)
    print(f"Failed to click element '{value}' after {max_attempts} attempts.")
    return False


def scroll_to_bottom(driver, pause=2):
    """Scroll to the bottom of the page (useful for infinite-scroll pages)."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(pause)
