# agentic-web-scraper/src/scraper_agent.py
"""A config-driven ("agentic") scraper: read plan -> navigate -> extract -> next page -> repeat."""

import time

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By

from data_models import Product
from driver_manager import DriverManager
from utils import robust_click, save_data_to_csv, save_data_to_json, wait_for_element


class ScraperAgent:
    """An agentic web scraper that operates based on a provided configuration."""

    def __init__(self, config, browser="chrome", headless=True):
        self.config = config
        self.driver_manager = DriverManager(browser_name=browser, headless=headless)
        self.driver = None
        self.scraped_products = []
        self.max_pages = config.get("max_pages", 5)
        self.delay = config.get("delay_between_pages", 2)

    # ---------- helpers ----------
    @staticmethod
    def _by_for(selector):
        """Selectors starting with '/' or '(' are XPath, everything else is CSS."""
        return By.XPATH if selector.startswith(("/", "(")) else By.CSS_SELECTOR

    def _get_element_text(self, parent, selector):
        """Safely get text from a child element (None if selector is null or not found)."""
        if not selector:
            return None
        try:
            return parent.find_element(self._by_for(selector), selector).text.strip() or None
        except (NoSuchElementException, StaleElementReferenceException):
            return None

    def _get_element_attribute(self, parent, selector, attribute):
        """Safely get an attribute (e.g. href, src) from a child element."""
        if not selector:
            return None
        try:
            value = parent.find_element(self._by_for(selector), selector).get_attribute(attribute)
            return value.strip() if value else None
        except (NoSuchElementException, StaleElementReferenceException):
            return None

    # ---------- perceive & extract ----------
    def _parse_product_data(self, item):
        """Build a Product from one item block using the selectors in the config."""
        s = self.config["item_data_selectors"]
        name = self._get_element_text(item, s.get("name"))
        price = self._get_element_text(item, s.get("price"))
        if not (name and price):  # minimum data for a valid product
            return None
        return Product(
            name=name,
            price=price,
            description=self._get_element_text(item, s.get("description")),
            url=self._get_element_attribute(item, s.get("url"), "href"),
            image_url=self._get_element_attribute(item, s.get("image_url"), "src"),
        )

    def scrape_page(self):
        """Extract every product on the current page."""
        container = self.config["item_container_selector"]
        wait_for_element(self.driver, self._by_for(container), container)  # explicit wait
        items = self.driver.find_elements(self._by_for(container), container)
        for item in items:
            product = self._parse_product_data(item)
            if product:
                self.scraped_products.append(product.to_dict())

    # ---------- act ----------
    def _go_to_next_page(self):
        """Click the 'next page' link. Returns False when there is no next page."""
        selector = self.config.get("pagination_selector")
        if not selector:
            return False
        by = self._by_for(selector)
        self.driver.implicitly_wait(0)  # don't wait 5s on the last page
        has_next = bool(self.driver.find_elements(by, selector))
        self.driver.implicitly_wait(5)
        if not has_next:
            return False
        old_url = self.driver.current_url
        if not robust_click(self.driver, by, selector):
            return False
        # wait until the page actually changes
        for _ in range(20):
            if self.driver.current_url != old_url:
                break
            time.sleep(0.25)
        return True

    # ---------- main loop ----------
    def run(self):
        """Run the agent loop and save the results."""
        self.driver = self.driver_manager.get_driver()
        if not self.driver:
            print("Failed to start the browser. Exiting.")
            return

        try:
            self.driver.get(self.config["start_url"])
            page = 1
            while page <= self.max_pages:
                print(f"Scraping page {page}...")
                self.scrape_page()
                if page == self.max_pages or not self._go_to_next_page():
                    break
                time.sleep(self.delay)  # rate limiting: be polite
                page += 1
        except Exception as e:
            print(f"An unexpected error occurred during scraping: {e}")
        finally:
            self.driver_manager.quit_driver()

        path = save_data_to_json(self.scraped_products, "scraped_products.json")
        save_data_to_csv(self.scraped_products, "scraped_products.csv")
        if path:
            print(f"Successfully scraped {len(self.scraped_products)} items and saved to {path}")
