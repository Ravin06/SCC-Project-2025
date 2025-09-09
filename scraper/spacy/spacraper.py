import re
import asyncio
from bs4 import BeautifulSoup
import spacy
from playwright.async_api import async_playwright
import urllib.parse
import subprocess, sys

# ----------------------
# Load NLP model
# ----------------------
subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
nlp = spacy.load("en_core_web_sm")

# ----------------------
# Extract name from email
# ----------------------
def extract_name_from_email(email):
    prefix = email.split('@')[0]
    parts = re.split(r'[._]', prefix)
    name = ' '.join([p.capitalize() for p in parts if p.isalpha()])
    return name

# ----------------------
# Extract info from text
# ----------------------
def extract_info_from_text(text):
    doc = nlp(text)
    names, orgs = [], []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            names.append(ent.text)
        elif ent.label_ == "ORG":
            orgs.append(ent.text)
    occupations_keywords = ["Engineer", "Manager", "Doctor", "Professor", "Developer", "Analyst"]
    occupations = [kw for kw in occupations_keywords if kw.lower() in text.lower()]
    return names, occupations, orgs

# ----------------------
# DuckDuckGo search with Playwright
# ----------------------
async def search_duckduckgo(query, num_results=5, debug=True):
    links = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        search_url = f"https://duckduckgo.com/?q={query}&t=h_&ia=web"
        await page.goto(search_url)
        if debug:
            print("[DEBUG] DuckDuckGo page loaded for query:", query)

        # Wait for results
        await page.wait_for_selector("a.result__a", timeout=10000)
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        for a in soup.select("a.result__a"):
            href = a.get("href")
            if not href:
                continue
            parsed = urllib.parse.urlparse(href)
            qs = urllib.parse.parse_qs(parsed.query)
            if "uddg" in qs:
                real_url = qs["uddg"][0]
                links.append(real_url)
            else:
                links.append(href)
            if len(links) >= num_results:
                break

        await browser.close()
    return links

# ----------------------
# Main OSINT function
# ----------------------
async def osint_from_email_and_username(email, username, debug=True):
    print(f"[INFO] Extracting info for email: {email} and username: {username}")

    email_prefix = email.split('@')[0]
    probable_name = extract_name_from_email(email)
    search_terms = [email_prefix, probable_name, username]

    all_links = []
    for term in search_terms:
        if not term:
            continue
        query = f"{term} site:linkedin.com OR site:github.com OR site:twitter.com OR site:facebook.com"
        if debug:
            print(f"[INFO] Searching DuckDuckGo for: {query}")
        links = await search_duckduckgo(query, debug=debug)
        if debug:
            print(f"[INFO] Found links for '{term}': {links}")
        all_links.extend(links)

    # Scrape text snippets
    all_text = " ".join(search_terms)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for link in all_links:
            try:
                await page.goto(link, timeout=10000)
                content = await page.content()
                soup = BeautifulSoup(content, "html.parser")
                text = soup.get_text(separator=' ', strip=True)
                all_text += " " + text[:1000]  # limit to first 1000 chars per site
            except Exception as e:
                if debug:
                    print(f"[WARN] Failed to scrape {link}: {e}")
                continue
        await browser.close()

    # Extract info
    names, occupations, orgs = extract_info_from_text(all_text)
    print("\n=== Results ===")
    print("Names found:", set(names) if names else "None")
    print("Occupations found:", set(occupations))
    print("Workplaces found:", set(orgs))

# ----------------------
# Run example
# ----------------------
email = "torvalds@linux-foundation.org"
username = "torvalds"
asyncio.run(osint_from_email_and_username(email, username))
