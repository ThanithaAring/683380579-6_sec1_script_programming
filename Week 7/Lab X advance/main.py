# agentic-web-scraper/main.py
"""Entry point: load the config (the agent's plan) and run the scraper agent."""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "src"))
os.chdir(BASE_DIR)  # so data/ is always created inside this project folder

from config_parser import ConfigParser
from scraper_agent import ScraperAgent


def main():
    """Load config and run the scraping agent."""
    config_file_path = os.path.join(BASE_DIR, "configs", "example_site_config.json")
    try:
        config = ConfigParser(config_file_path).load_config()
        # headless=False -> you can watch the browser click through the pages
        agent = ScraperAgent(config, browser="chrome", headless=True)
        agent.run()
    except FileNotFoundError as e:
        print(f"Configuration file error: {e}")
    except ValueError as e:
        print(f"Configuration validation error: {e}")


if __name__ == "__main__":
    main()
