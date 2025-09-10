import re
import requests
from bs4 import BeautifulSoup
import spacy
import urllib.parse
import subprocess, sys
from playwright.sync_api import sync_playwright

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
# DuckDuckGo HTML search
# ----------------------
def search_duckduckgo_html(query, num_results=5):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Go to DuckDuckGo search
        page.goto(f"https://duckduckgo.com/?q={query}", timeout=60000)

        # Wait for results or timeout gracefully
        try:
            page.wait_for_selector("a.result__a", timeout=15000)
        except:
            print(f"[WARN] No results found for query: {query}")
            browser.close()
            return []

        # Extract links
        links = []
        for a in page.query_selector_all("a.result__a"):
            href = a.get_attribute("href")
            if href and href.startswith("http"):
                links.append(href)
            if len(links) >= num_results:
                break

        browser.close()
        return links
# ----------------------
# Main OSINT function
# ----------------------
def osint_from_email_and_username_requests(email, username, ):
    print(f"[INFO] Extracting info for email: {email} and username: {username}")

    email_prefix = email.split('@')[0]
    probable_name = extract_name_from_email(email)
    search_terms = [email_prefix, probable_name, username]

    all_links = []
    for term in search_terms:
        if not term:
            continue
        # HTML DuckDuckGo works better with simpler queries (avoid OR)
        query = f"{term} site:linkedin.com OR site:github.com OR site:twitter.com OR site:facebook.com"
        # Replace OR with simple multiple queries separated by spaces
        query = query.replace(" OR ", " ")

        links = search_duckduckgo_html(query)

        all_links.extend(links)

    # Filter relevant links
    relevant_links = [l for l in all_links if "github.com" in l or "linkedin.com/in/" in l]

    all_text = " ".join(search_terms)
    headers = {"User-Agent": "Mozilla/5.0"}

    for link in relevant_links:
        try:
            r = requests.get(link, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            text = ""
            if "github.com" in link:
                desc = soup.select_one("meta[name='description']")
                if desc:
                    text += desc.get("content", "")
                readme = soup.select_one("article.markdown-body")
                if readme:
                    text += " " + readme.get_text(separator=" ", strip=True)
            elif "linkedin.com/in/" in link:
                headline = soup.select_one("title")
                if headline:
                    text += headline.get_text(separator=" ", strip=True)

            if text:
                all_text += " " + text[:1000]

        except Exception as e:

            continue

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
osint_from_email_and_username_requests(email, username)
