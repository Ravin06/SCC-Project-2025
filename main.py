from urllib import response
from dotenv import load_dotenv
import os
import re
import smtplib
import google.generativeai as genai
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from faker import Faker
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from prompt import email_prompt

load_dotenv()
api_key = os.getenv("GEMINI_KEY")
if not api_key:
    raise RuntimeError("GEMINI_KEY environment variable not set")
genai.configure(api_key=api_key)

fake = Faker()
ua = UserAgent()

def generate_dynamic_email_content(name, personality="formal"):
    prompt = email_prompt.format(name=name, personality=personality)
    model = genai.GenerativeModel("gemini-2.0-flash")
    global subject
    response = model.generate_content(prompt)
    subject = response.text.strip()
    body = response.text.strip()
    body_update = re.sub(r"(?:<subject>|subject|phishing subject)\s*:\s*[^\n\r]+", "", body, flags=re.IGNORECASE).strip()
    print(f"\nGenerated Email Content:\n{body}\n")
    return body_update

def perform_osint_scraping(name):
    """
    Perform basic OSINT scraping by searching for the person's name on Google
    and extracting publicly available information like social media links, occupation, etc.
    """
    search_query = f"{name} site:linkedin.com OR site:twitter.com OR site:github.com"
    headers = {
        'User-Agent': ua.random
    }

    google_url = f"https://www.google.com/search?q={search_query}"
    response = requests.get(google_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        result_links = soup.find_all('a', href=True)

        social_media_links = []
        for link in result_links:
            href = link['href']
            if 'linkedin.com/in' in href:
                social_media_links.append({'platform': 'LinkedIn', 'url': href})
            elif 'twitter.com' in href:
                social_media_links.append({'platform': 'Twitter', 'url': href})
            elif 'github.com' in href:
                social_media_links.append({'platform': 'GitHub', 'url': href})

        snippets = soup.find_all('div', {'class': 'BNeawe iBp4i AP7Wnd'})
        occupation = None
        company = None
        for snippet in snippets:
            text = snippet.get_text()
            if "Software Engineer" in text:
                occupation = "Software Engineer"
            if "Tech Company" in text:
                company = "Tech Company"

        return {
            'occupation': occupation or 'Not found',
            'company': company or 'Not found',
            'social_media': social_media_links
        }

    else:
        print(f"Error fetching data from Google. Status Code: {response.status_code}")
        return {}

def send_spoofed_email(target_email, subject, body, from_email, from_password, spoofed_from):
    msg = MIMEMultipart()
    msg['From'] = spoofed_from
    msg['To'] = target_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        
        text = msg.as_string()
        server.sendmail(from_email, target_email, text)
        server.quit()
        print(f"Email sent to {target_email} successfully! (Spoofed From: {spoofed_from})")
    except Exception as e:
        print(f"Error sending email to {target_email}: {e}")

def generate_random_sender():
    random_name = fake.name()
    random_email = fake.email()
    return random_email

# Main function to execute the tool
def main():
    target_name = input("Enter the target's name: ")
    target_email = input("Enter the target's email: ")
    from_email = input("Enter your real email (used for SMTP login): ")
    from_password = input("Enter your email password: ")
    personality = input("Enter personality type (formal, friendly, urgent, casual, suspicious): ").lower()

    # Perform OSINT lookup for the target's name (doesnt work yet)
    osint_results = perform_osint_scraping(target_name)

    print(f"\nOSINT Results for {target_name}:")
    print(f"Occupation: {osint_results.get('occupation', 'Not available')}")
    print(f"Company: {osint_results.get('company', 'Not available')}")
    print("Social Media Links:")
    for social in osint_results.get('social_media', []):
        print(f"- {social['platform']}: {social['url']}")

    spoofed_from = generate_random_sender()
    # Generate dynamic phishing content based on personality
    phishing_body = generate_dynamic_email_content(target_name, personality)
    # Customize phishing email content with OSINT data
    phishing_body = phishing_body.replace("[Fake Link]", osint_results['social_media'][0]['url'] if osint_results['social_media'] else "[Fake Link]")
    # Generate phishing subject
    # TODO: make this dynamic based on gemini
    # phishing_subject = f"Urgent: Account Verification Needed - {osint_results['company']}"
    # regex to capture subject line (case-insensitive, ignores spaces)
    match = re.search(r"(?:<subject>|subject|phishing subject)\s*:\s*(.+)", 
        subject, re.IGNORECASE)
    print(f"Regex Match: {match}")
    phishing_subject = match.group(1).strip() if match else None
    print(f"Phishing Subject: {phishing_subject}")
    send_spoofed_email(target_email, phishing_subject, phishing_body, from_email, from_password, spoofed_from) #sends mail, spoofing doesnt work either i think

if __name__ == "__main__":
    print("Starting Phishing Tool...\n")
    main()
