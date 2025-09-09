import re
import requests
from bs4 import BeautifulSoup
import spacy
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
# DuckDuckGo HTML search
# ----------------------
def search_duckduckgo_html(query, num_results=5, debug=True):
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    headers = {    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
    r = requests.get(url, headers=headers, timeout=10)
    if debug:
        print(f"[DEBUG] URL requested: {url}")
        print(f"[DEBUG] Response status: {r.status_code}")
        print(f"[DEBUG] First 500 chars of HTML:\n{r.text[:500]}\n")
    soup = BeautifulSoup(r.text, "html.parser")
    links = []

    for a in soup.select("a.result__a"):
        href = a.get("href")
        if not href:
            continue
        # DuckDuckGo redirects sometimes, decode if necessary
        parsed = urllib.parse.urlparse(href)
        qs = urllib.parse.parse_qs(parsed.query)
        if "uddg" in qs:
            links.append(qs["uddg"][0])
        else:
            links.append(href)
        if len(links) >= num_results:
            break
    return links

# ----------------------
# Main OSINT function
# ----------------------
def osint_from_email_and_username_requests(email, username, debug=True):
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
        if debug:
            print(f"[INFO] Searching DuckDuckGo HTML for: {query}")
        links = search_duckduckgo_html(query, debug=debug)
        if debug:
            print(f"[INFO] Found links for '{term}': {links}")
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
            if debug:
                print(f"[WARN] Failed to scrape {link}: {e}")
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
