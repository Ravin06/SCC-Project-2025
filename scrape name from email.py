import csv
import re

def extract_name_from_email(email):
    username = email.split("@")[0]
    username = re.sub(r"\d+", "", username)
    username = re.sub(r"[._-]+", " ", username)
    return " ".join(word.capitalize() for word in username.split())

with open("database.csv.example", "r", newline="") as infile:
    rows = []
    reader = csv.reader(infile)
    for row in reader:
        if not row:
            continue
        email = row[0].strip()
        name = row[1].strip() if len(row) > 1 and row[1] else extract_name_from_email(email)
        rows.append([email, name])

with open("database.csv.example", "w", newline="") as outfile:
    writer = csv.writer(outfile)
    writer.writerows(rows)
