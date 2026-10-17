# Advanced Web Scraping & Introduction to Automated Agents

A config-driven ("agentic") product scraper built with **Selenium**. The agent reads a JSON plan, opens a real browser, extracts product data, clicks "next page", and repeats until there are no more pages or `max_pages` is reached. Results are saved to `data/scraped_products.json` (and `.csv`).

Target site: [books.toscrape.com](https://books.toscrape.com) — a sandbox site made for scraping practice.

## Key Concepts Demonstrated

* **Selenium**: real browser control (headless or visible) for JavaScript-rendered pages.
* **WebDriver management**: `webdriver-manager`, with Selenium's built-in driver manager as a fallback.
* **Config-driven agent**: what to scrape and how to paginate lives in `configs/example_site_config.json`, so a new site needs only a new config.
* **Robustness**: implicit + explicit waits (`WebDriverWait`), retry on click (`robust_click`), safe element lookups.
* **Structured data**: `Product` dataclass, saved to JSON and CSV.
* **Polite scraping**: delay between pages, page limit.

## Setup & How to Run

1. Clone and enter the project:
   ```bash
   git clone https://github.com/YOUR_USERNAME/agentic-web-scraper.git
   cd agentic-web-scraper
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate          # macOS/Linux: source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Make sure **Google Chrome** (or Firefox) is installed.
4. Run (from inside the `agentic-web-scraper` folder):
   ```bash
   python main.py
   ```
   Expected output:
   ```
   Scraping page 1...
   Scraping page 2...
   Successfully scraped 40 items and saved to data\scraped_products.json
   ```

## Config Fields

| Field | Meaning |
|---|---|
| `start_url` | First page to open |
| `max_pages` | Maximum number of pages to scrape |
| `delay_between_pages` | Seconds to wait between pages |
| `item_container_selector` | Selector for one product block |
| `pagination_selector` | Selector for the "next page" link (`null` = single page) |
| `item_data_selectors` | Selectors for each field inside a product block (`null` = not on page) |

Selectors are CSS by default; a selector starting with `/` is treated as XPath.

## Project Structure

```
agentic-web-scraper/
├── src/
│   ├── __init__.py
│   ├── scraper_agent.py     # Agent loop: navigate, extract, paginate
│   ├── config_parser.py     # Load and validate the JSON config
│   ├── data_models.py       # Product dataclass
│   ├── utils.py             # Save JSON/CSV, explicit waits, robust click
│   └── driver_manager.py    # Selenium WebDriver setup/teardown
├── configs/
│   └── example_site_config.json
├── data/                    # Output (created after running)
├── docs/
│   └── ETHICS.md
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Debugging

* **`can't open file ... main.py`**: you are in the wrong folder — `cd agentic-web-scraper` first.
* **WebDriver / SessionNotCreated errors**: update Chrome; the driver is downloaded automatically.
* **0 items scraped**: re-check selectors with DevTools (F12).
* **Want to see the browser?** Set `headless=False` in `main.py`.

See [docs/ETHICS.md](docs/ETHICS.md) for ethical and legal guidelines. **For educational purposes only.**
