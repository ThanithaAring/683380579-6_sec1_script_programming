# agentic-web-scraper/src/driver_manager.py
"""Manages Selenium WebDriver setup and teardown."""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

USER_AGENTS = {
    "chrome": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
}


class DriverManager:
    """Creates and closes Selenium WebDriver instances (Chrome or Firefox)."""

    def __init__(self, browser_name="chrome", headless=True):
        self.browser_name = browser_name.lower()
        self.headless = headless
        self.driver = None

    def _make_service(self, service_class, manager_class):
        """Try webdriver-manager first; fall back to Selenium's built-in driver manager."""
        try:
            return service_class(manager_class().install())
        except Exception as e:
            print(f"webdriver-manager failed ({e}). Using Selenium's built-in driver manager.")
            return service_class()

    def get_driver(self):
        """Initialize and return a WebDriver instance (or None if setup fails)."""
        if self.driver:
            return self.driver

        try:
            if self.browser_name == "chrome":
                from webdriver_manager.chrome import ChromeDriverManager

                options = webdriver.ChromeOptions()
                if self.headless:
                    options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--log-level=3")  # hide Chrome console logs
                options.add_argument(f"user-agent={USER_AGENTS['chrome']}")
                service = self._make_service(ChromeService, ChromeDriverManager)
                self.driver = webdriver.Chrome(service=service, options=options)

            elif self.browser_name == "firefox":
                from webdriver_manager.firefox import GeckoDriverManager

                options = webdriver.FirefoxOptions()
                if self.headless:
                    options.add_argument("--headless")
                options.set_preference("general.useragent.override", USER_AGENTS["firefox"])
                service = self._make_service(FirefoxService, GeckoDriverManager)
                self.driver = webdriver.Firefox(service=service, options=options)

            else:
                raise ValueError(f"Unsupported browser: {self.browser_name}. Choose 'chrome' or 'firefox'.")

        except ValueError:
            raise
        except Exception as e:
            print(f"Error setting up {self.browser_name} driver: {e}")
            print(f"Make sure {self.browser_name.title()} is installed.")
            return None

        self.driver.implicitly_wait(5)  # implicit wait: up to 5 seconds when finding elements
        return self.driver

    def quit_driver(self):
        """Close the browser if it is running."""
        if self.driver:
            self.driver.quit()
            self.driver = None
