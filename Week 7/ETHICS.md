# Web Scraping Ethics and Legality Guidelines

## 1. Respect `robots.txt`
Check `https://<domain>/robots.txt` before scraping and do not scrape paths it disallows.

## 2. Review Terms of Service
If a site's Terms of Service forbid scraping, scraping it can be a breach of contract and may lead to a Cease and Desist letter or legal action.

## 3. Be Polite: Rate Limiting
Too many requests too fast can slow down or crash a server. This project waits between pages (`delay_between_pages`) and stops after `max_pages`.

## 4. Identify Yourself
Use an honest User-Agent where possible, so site owners can contact you if there is a problem.

## 5. Selenium Is Seen Differently
A real browser loads every image, script and stylesheet, which is heavier for the server than a simple request. Some sites treat automated browsers as bots and block them. Use Selenium only when the page really needs JavaScript.

## 6. Data Usage and Copyright
Scraped content is often copyrighted. Do not republish or sell it without permission, and never collect personal information without consent.

## 7. Risks
IP blocking, CAPTCHAs, account bans and legal action. When in doubt, ask the website owner for permission or use an official API.

This project scrapes **books.toscrape.com**, a site built specifically for scraping practice.
