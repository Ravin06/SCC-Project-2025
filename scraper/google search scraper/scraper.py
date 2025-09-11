from serpapi import GoogleSearch
import os
import json
import urllib.parse

API_KEY = "a6c7ba97f266a40363d388caed4f5b793cdafb24cecb42daabcf603b81df3726"

# Email + usernames
email = "mark.zuckerberg@gmail.com"


# Extract the part before @
prefix = email.split("@")[0]

# Remove digits
prefix_no_digits = "".join([c for c in prefix if not c.isnumeric()])

# Replace dots with spaces (optional)
google_username = prefix_no_digits.replace(".", " ")
email_username = prefix


# Platforms to search
platforms = [
    "linkedin.com",   # Professional profiles
    "github.com",     # Code repositories
    "twitter.com",    # Social media
    "facebook.com",   # Social media
    "instagram.com",  # Social media / photos
    "pinterest.com",  # Social / creative
    "reddit.com",     # Forums / discussions
    "medium.com",     # Blogs / articles
    "youtube.com",    # Videos / channels
    "quora.com",      # Q&A / discussions
    "stackexchange.com", # Q&A / professional
    "stackoverflow.com", # Q&A for developers
    "tiktok.com",     # Social videos
    "behance.net",    # Creative portfolios
    "dribbble.com",   # Design portfolios
    "angel.co",       # Startup / professional profiles
    "flickr.com",     # Photos
    "slideshare.net"  # Presentations
]


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
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "osint_results.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2)

print(f"Results saved: {len(all_results)} profiles found.")