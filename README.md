# Phishing Tool - SCC Project 2025
by: Ravin, Royston, Zhang Di, Charmine, Yu Kai
## Overview
This phishing tool is designed to generate and send spoofed emails based on Open-Source Intelligence (OSINT) results. It uses several tools such as GHunt, Holehe, Toutatis, Sherlock, and fakedata to gather information about the target and create dynamic phishing emails. The tool leverages Google's Generative AI (Gemini) to dynamically generate email content.

## Features
- OSINT Scraping: Collects publicly available information about the target, such as occupation, company, and social media profiles.
- Phishing Email Generation: Creates realistic phishing emails with HTML and plain text content.
- Spoofed Email Sending: Sends spoofed emails using an SMTP server. (have to setup your own)
- Multiple Input Options:
  - Process a single target email.
  - Process multiple emails from a CSV file (`database.csv`).
- Tool Integration: Integrates several OSINT tools:
  - GHunt for Google-related data.
  - Holehe for email lookup.
  - Toutatis for username lookup.
  - Sherlock for social media username enumeration.
- Customizable Email: The email's content can be adjusted based on the target's personality type (formal, casual, suspicious, etc.).

## Requirements
- Python 3.7+
- Libraries:
  - `dotenv`: For loading environment variables.
  - `requests`: To send HTTP requests.
  - `beautifulsoup4`: To scrape web content.
  - `smtplib`: To send emails.
  - `google-generativeai`: For generating dynamic email content using Google's Generative AI (Gemini).
  - `fake_useragent`: For randomizing user-agent headers.
  - `Faker`: To generate random names and emails.
  - `subprocess`: For running OSINT tools (ghunt, holehe, toutatis, sherlock).
```bash
pip install -r requirements.txt
```
- External Tools:
  - `ghunt`: Google OSINT tool.
  - `holehe`: Email OSINT tool.
  - `toutatis`: Username OSINT tool.
  - `sherlock`: Username OSINT tool.
 
## Setup
1. Clone the Repository:
```bash
git clone https://github.com/Ravin06/SCC-Project-2025.git
cd SCC-Project-2025
```

2. Set up Environment Variables:
Create a `.env` file in the root directory and add your GEMINI_KEY (Google's Gemini API key) as follows:
```bash
GEMINI_KEY=your-gemini-api-key
```

3. Install Dependencies:
Install the required libraries by running:
```bash
pip install -r requirements.txt
```

4. Install External Tools:
Make sure that the following tools are installed and available in your system's PATH:

ghunt (https://github.com/mxrch/ghunt)  
holehe (https://github.com/megadose/holehe)  
toutatis (https://github.com/megadose/toutatis)  
sherlock (https://github.com/sherlock-project/sherlock)  

## Usage
Running the Tool
1. Single Email Process:
- To process a single target email, choose the option 1 when prompted, and provide the target's email and username (optional).

2. Multiple Email Process (CSV):
- To process multiple emails from a CSV file (database.csv), choose the option 2. The tool will process each row of the CSV (email in the first column).

### Example Run:
```bash
$ python phishing_tool.py
Starting Phishing Tool...

Enter your real email (used as sender for SMTP): your-email@gmail.com
Enter your email password (or app-specific password for Gmail): **********
Enter personality type (formal, friendly, urgent, casual, suspicious): formal
Choose input method (1 for single email, 2 for database.csv): 1
Enter the target's email: target-email@example.com
Enter the target's username (optional, press Enter to skip): targetusername
```

The tool will:
- Run OSINT checks using GHunt, Holehe, Toutatis, and Sherlock.
- Generate dynamic email content based on the target’s personality.
- Send the spoofed email using SMTP.

### Tool Features:
- OSINT Results: Displays occupation, company, and social media links found for the target.
- Phishing Email Generation: Creates an email with a subject and body tailored to the target.
- Spoofed Email Sending: Sends the generated email to the target.

## Contributing
Feel free to contribute to this project! If you have ideas or improvements, open an issue or submit a pull request. Please make sure to follow the coding style and include tests where applicable.
### Future Development (ill do it when i get time maybe)
- SMS and Voice Phishing after phone number OSINT
- Possible commercial GUI (https://studio.firebase.google.com/studio-9890097031)
and more!

## Disclaimer
This tool is for educational purposes only. The usage of phishing techniques without proper authorization is illegal and unethical. Ensure you have explicit consent before conducting any form of penetration testing or phishing campaigns. Misuse of this tool may lead to legal consequences. Always comply with ethical guidelines and local laws.
