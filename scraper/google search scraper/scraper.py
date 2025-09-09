from serpapi import GoogleSearch
import os
import json

API_KEY = "a6c7ba97f266a40363d388caed4f5b793cdafb24cecb42daabcf603b81df3726"

# Email + usernames
email = "johndoe@gmail.com"
google_username = "alexsteve"

# Extract username part from email
email_username = email.split("@")[0]

# Platforms to search
platforms = ["linkedin.com", "github.com", "twitter.com"]

# Combine search terms
usernames = [email_username, google_username]

# Collect results
all_results = []

for user in usernames:
    for platform in platforms:
        query = f"{user} site:{platform}"
        params = {
            "engine": "google",
            "q": query,
            "api_key": API_KEY,
            "num": "10",
            "gl": "sg",   # Singapore
            "hl": "en"
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        # Extract organic results URLs
        if "organic_results" in results:
            for res in results["organic_results"]:
                link = res.get("link")
                if link:
                    all_results.append({"username": user, "platform": platform, "url": link})

# Save results to JSON
with open("osint_results.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2)

print(f"Results saved: {len(all_results)} profiles found.")