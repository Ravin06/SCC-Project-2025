from dotenv import load_dotenv
import os
import smtplib
import google.generativeai as genai
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from faker import Faker
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from prompt import email_prompt, plain_text_email_prompt
import subprocess
import re
import json

load_dotenv()
api_key = os.getenv("GEMINI_KEY")
if not api_key:
    raise RuntimeError("GEMINI_KEY environment variable not set")
genai.configure(api_key=api_key)

fake = Faker()
ua = UserAgent()

def generate_dynamic_email_content(name, personality="formal", osint_results={}):
    # First, try to generate an HTML email
    html_prompt = email_prompt.format(
        name=name,
        personality=personality,
        company=osint_results.get('company', 'Not found'),
        occupation=osint_results.get('occupation', 'Not found')
    )
    model = genai.GenerativeModel("gemini-2.0-flash")

    for _ in range(2):
        response = model.generate_content(html_prompt)
        content = response.text.strip()
        try:
            # The response is sometimes wrapped in ```json ... ```, so we remove that.
            if content.startswith("```json"):
                content = content[7:-3]
            email_data = json.loads(content)
            subject = email_data['subject']
            body = email_data['body']
            if body.startswith("<!DOCTYPE html>") and body.endswith("</html>"):
                return subject, body
        except (json.JSONDecodeError, KeyError):
            # If parsing fails or keys are missing, we try again.
            continue

    # Fallback to plain text email
    print("HTML email generation failed. Falling back to plain text.")
    plain_text_prompt_formatted = plain_text_email_prompt.format(
        name=name,
        personality=personality,
        company=osint_results.get('company', 'Not found'),
        occupation=osint_results.get('occupation', 'Not found')
    )
    response = model.generate_content(plain_text_prompt_formatted)
    content = response.text.strip()
    try:
        if content.startswith("```json"):
            content = content[7:-3]
        email_data = json.loads(content)
        return email_data['subject'], email_data['body']
    except (json.JSONDecodeError, KeyError):
        # If fallback also fails, return a default email.
        return "Urgent: Account Verification Needed", f"""Dear {name},

We have detected some unusual activity on your account. Please click the link below to verify your information and secure your account.

[Fake Link]

Thank you for your attention to this matter.

Best regards,
Your Trusted Service Provider."""

def perform_osint_scraping(name, email):
    """
    Perform basic OSINT scraping by searching for the person's name on Google
    and extracting publicly available information like social media links, occupation, etc.
    """
    domain = email.split('@')[1]
    search_query = f'\"_name_\" {domain}'
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
            # This is a very basic way to extract info, can be improved
            if any(keyword in text.lower() for keyword in ['engineer', 'developer', 'manager']):
                occupation = text
            if domain.split('.')[0].lower() in text.lower():
                company = domain.split('.')[0]

        return {
            'occupation': occupation or 'Not found',
            'company': company or 'Not found',
            'social_media': social_media_links
        }

    else:
        print(f"Error fetching data from Google. Status Code: {response.status_code}")
        return {}

def send_spoofed_email(target_email, subject, body, from_email, from_password, spoofed_name, spoofed_email):
    msg = MIMEMultipart()
    msg['From'] = formataddr((spoofed_name, spoofed_email))
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
        print(f"Email sent to {target_email} successfully! (Spoofed From: {spoofed_name} <{spoofed_email}>)")
    except Exception as e:
        print(f"Error sending email to {target_email}: {e}")

def generate_random_sender():
    random_name = fake.name()
    random_email = fake.email()
    return random_name, random_email

def perform_ghunt_osint(email):
    try:
        print("Running ghunt on the email...")
        result = subprocess.run(['ghunt', 'email', email], capture_output=True, text=True, timeout=60)
        print("ghunt scan complete.")
        return result.stdout
    except subprocess.TimeoutExpired:
        return "ghunt scan timed out after 60 seconds."
    except FileNotFoundError:
        return "ghunt not found. Please make sure it is installed and in your PATH."
    except Exception as e:
        return f"An error occurred during ghunt scan: {e}"

def extract_name_from_ghunt(ghunt_output):
    lines = ghunt_output.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("[+] Found other names used by the target :") and i + 1 < len(lines):
            return lines[i+1].strip()
    for line in lines:
        if line.startswith("Name:"):
            return line.split("Name:")[1].strip()
    return None

def main():
    target_email = input("Enter the target's email: ")
    #to be removed later, save the email and password in .env file
    from_email = input("Enter your real email (used for SMTP login): ")
    from_password = input("Enter your email password: ")
    #continue from here
    personality = input("Enter personality type (formal, friendly, urgent, casual, suspicious): ").lower()

    # Perform ghunt OSINT on the email
    ghunt_results = perform_ghunt_osint(target_email)
    target_name = extract_name_from_ghunt(ghunt_results)

    if not target_name:
        print("Could not extract name from ghunt output. Please enter the name manually.")
        target_name = input("Enter the target's name: ")

    # Perform OSINT lookup for the target's name
    osint_results = perform_osint_scraping(target_name, target_email)

    print(f"\nOSINT Results for {target_name}:")
    print(f"Occupation: {osint_results.get('occupation', 'Not available')}")
    print(f"Company: {osint_results.get('company', 'Not available')}")
    print("Social Media Links:")
    for social in osint_results.get('social_media', []):
        print(f"- {social['platform']}: {social['url']}")

    print("\nGHunt OSINT Results:")
    print(ghunt_results)

    spoofed_name, spoofed_email = generate_random_sender()
    # Generate dynamic phishing content based on personality
    phishing_subject, phishing_body = generate_dynamic_email_content(target_name, personality, osint_results)
    phishing_body = phishing_body.replace("[Fake Link]", "<a href=\"https://www.youtube.com/watch?v=dQw4w9WgXcQ\">Click here to verify</a>")
    
    send_spoofed_email(target_email, phishing_subject, phishing_body, from_email, from_password, spoofed_name, spoofed_email)

if __name__ == "__main__":
    print("Starting Phishing Tool...\n")
    main()
