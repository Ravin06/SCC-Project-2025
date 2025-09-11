from dotenv import load_dotenv
import os
import csv
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
from datetime import datetime, timedelta

load_dotenv()
api_key = os.getenv("GEMINI_KEY")
if not api_key:
    raise RuntimeError("GEMINI_KEY environment variable not set")
genai.configure(api_key=api_key)

fake = Faker()
ua = UserAgent()

def generate_dynamic_email_content(name, personality="formal", osint_results={}, logo_url=None):
    expiration_time = datetime.now() + timedelta(hours=24)
    expiration_str = expiration_time.strftime("%A, %B %d, %Y")
    #Generate a HTML email
    html_prompt = email_prompt.format(
        name=name,
        personality=personality,
        company=osint_results.get('company', 'Not found'),
        occupation=osint_results.get('occupation', 'Not found'),
        expiration_time=expiration_str,
        logo_url=logo_url
    )
    model = genai.GenerativeModel("gemini-2.0-flash")

    for _ in range(2):
        response = model.generate_content(html_prompt)
        content = response.text.strip()
        try:
            #The response is sometimes wrapped in ```json ... ```, so we remove that.
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

    # Fallback to plain text email if HTML fails
    print("HTML email generation failed. Falling back to plain text.")
    plain_text_prompt_formatted = plain_text_email_prompt.format(
        name=name,
        personality=personality,
        company=osint_results.get('company', 'Not found'),
        occupation=osint_results.get('occupation', 'Not found'),
        expiration_time=expiration_str
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
        expiration_time = datetime.now() + timedelta(hours=24)
        expiration_str = expiration_time.strftime("%A, %B %d, %Y")
        return "Urgent: Account Verification Needed", f"""Dear {name},

We have detected unusual activity on your account that requires immediate attention. To prevent potential unauthorized access, please verify your account details as soon as possible.

Failure to verify your account before {expiration_str} may result in temporary suspension.

Click here to verify your account immediately: [Fake Link]

Thank you for your attention to this matter.

Best regards,
Your Trusted Service Provider.

This is an automated message, please do not reply. Report Scam"""

def perform_osint_scraping(name, email):
    #basic osint scraping (unused in final version)
    domain = email.split('@')[1]
    search_query = f'"_name_" {domain}'
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

#sending spoofed email duh as per func name
def send_spoofed_email(target_email, subject, html_body, text_body, from_email, from_password, spoofed_name, spoofed_email):
    msg = MIMEMultipart('alternative')
    #email deets
    msg['From'] = formataddr((spoofed_name, spoofed_email))
    msg['To'] = target_email
    msg['Subject'] = subject

    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

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

#random ahhhh name
def generate_random_sender():
    random_name = fake.name()
    random_email = f"{random_name.replace(' ', '.').lower()}@dbs.com"
    return random_name, random_email

#its ghunting time or smt
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

#its holeheing time heehee
def perform_holehe_osint(email):
    try:
        print("Running holehe on the email...")
        result = subprocess.run(['holehe', email], capture_output=True, text=True, timeout=60)
        print("holehe scan complete.")
        return result.stdout
    except subprocess.TimeoutExpired:
        return "holehe scan timed out after 60 seconds."
    except FileNotFoundError:
        return "holehe not found. Please make sure it is installed and in your PATH."
    except Exception as e:
        return f"An error occurred during holehe scan: {e}"

#its toutatising time teehee
def perform_toutatis_osint(username):
    try:
        print("Running Toutatis on the username...")
        session_id = "32303133574%3AbxGWvrADdCPFCT%3A24%3AAYjoJh8VeUCKYKfviKoSZMLhtCZnyMh7W6rzBE6Rvn0"
        result = subprocess.run(['toutatis', '-u', username, '-s', session_id], capture_output=True, text=True, timeout=60)
        print("Toutatis scan complete.")
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Toutatis scan timed out after 60 seconds."
    except FileNotFoundError:
        return "Toutatis not found. Please make sure it is installed."
    except Exception as e:
        return f"An error occurred during Toutatis scan: {e}"

#its sherlocking time weehee
def perform_sherlock_osint(username):
    try:
        print("Running Sherlock on the username...")
        result = subprocess.run(['sherlock', '--print-found', username], capture_output=True, text=True, timeout=300)
        print("Sherlock scan complete.")
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Sherlock scan timed out after 300 seconds."
    except FileNotFoundError:
        return "Sherlock not found. Please make sure it is installed and in your PATH."
    except Exception as e:
        return f"An error occurred during Sherlock scan: {e}"

def extract_name_from_ghunt(ghunt_output):
    lines = ghunt_output.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("[+] Found other names used by the target :") and i + 1 < len(lines):
            return lines[i+1].strip()
    for line in lines:
        if line.startswith("Name:"):
            return line.split("Name:")[1].strip()
    return None

#extract name from toutatis output in the case that ghunt fails
def extract_name_from_toutatis(toutatis_output):
    for line in toutatis_output.splitlines():
        if "Full Name" in line:
            return line.split(":")[1].strip()
    return None


def process_email(target_email, from_email, from_password, personality, target_username=None, logo_url=None):
    #ghunt OSINT
    ghunt_results = perform_ghunt_osint(target_email)
    target_name = extract_name_from_ghunt(ghunt_results)
    #holehe OSINT
    holehe_results = perform_holehe_osint(target_email)

    toutatis_results = ""
    if target_username:
        toutatis_results = perform_toutatis_osint(target_username)

    if not target_name and target_username:
        print("Could not extract name from ghunt output, trying with Toutatis.")
        target_name = extract_name_from_toutatis(toutatis_results)

    if not target_name and target_username:
        print("Could not extract name from ghunt or toutatis output, using provided username.")
        target_name = target_username

    if not target_name:
        print("Could not extract name from ghunt or toutatis output. Please enter the name manually.")
        target_name = input(f"Enter the target's name for {target_email}: ")

    #osint lookup name
    osint_results = perform_osint_scraping(target_name, target_email)

    print(f"\nOSINT Results for {target_name}:")
    print(f"Occupation: {osint_results.get('occupation', 'Not available')}")
    print(f"Company: {osint_results.get('company', 'Not available')}")
    print("Social Media Links:")
    for social in osint_results.get('social_media', []):
        print(f"- {social['platform']}: {social['url']}")

    print("\nGHunt OSINT Results:")
    print(ghunt_results)

    print("\nHolehe OSINT Results:")
    print(holehe_results)

    if target_username:
        print("\nToutatis OSINT Results:")
        print(toutatis_results)

        print("\nSherlock OSINT Results:")
        sherlock_results = perform_sherlock_osint(target_username)
        print(sherlock_results)

    spoofed_name, spoofed_email = generate_random_sender()
    #dynamic email content generation
    phishing_subject, phishing_body_html = generate_dynamic_email_content(target_name, personality, osint_results, logo_url)
    phishing_body_html = phishing_body_html.replace("[Fake Link]", "https://9000-firebase-studio-1757601280967.cluster-va5f6x3wzzh4stde63ddr3qgge.cloudworkstations.dev/?monospaceUid=174392")

    #convert HTML to plain text for email clients that do not support HTML
    soup = BeautifulSoup(phishing_body_html, 'html.parser')
    phishing_body_text = soup.get_text()

    send_spoofed_email(target_email, phishing_subject, phishing_body_html, phishing_body_text, from_email, from_password, spoofed_name, spoofed_email)

def main():
    # with open("database.csv", "r") as csvfile:
    #     reader = csv.reader(csvfile)
    #     for row in reader:
    #         target_name = row[0]
    #         target_email = row[1]
    while True:
        from_email = input("Enter your real email (used as sender for SMTP): ")
        if '@' in from_email:
            break
        else:
            print("Invalid email address. Please enter a valid email.")
    from_password = input("Enter your email password (or app-specific password for Gmail): ")
    personality = input("Enter personality type (formal, friendly, urgent, casual, suspicious): ").lower()
    logo_url = "https://upload.wikimedia.org/wikipedia/en/thumb/b/b1/DBS_Bank_Logo_%28alternative%29.svg/579px-DBS_Bank_Logo_%28alternative%29.svg.png?20250831083221"

    choice = input("Choose input method (1 for single email, 2 for database.csv): ")

    if choice == '1':
        target_email = input("Enter the target's email: ")
        target_username = input("Enter the target's username (optional, press Enter to skip): ")
        process_email(target_email, from_email, from_password, personality, target_username, logo_url)
    elif choice == '2':
        try:
            with open("database.csv", "r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row: #handle empty rows
                        target_email = row[0] #email is in the first column
                        print(f"\nProcessing email from database: {target_email}")
                        process_email(target_email, from_email, from_password, personality, logo_url=logo_url)
        except FileNotFoundError:
            print("Error: database.csv not found.")
    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    print("Starting Phishing Tool...\n")
    main()
