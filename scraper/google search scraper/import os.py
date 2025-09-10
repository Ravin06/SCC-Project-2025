

import os
import json
import re
from nameparser import HumanName
from huggingface_hub import InferenceClient

# ----------------------
# Initialize HF client
# ----------------------
HF_TOKEN = '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'
if not HF_TOKEN:
    raise ValueError("Please set your Hugging Face API token in the HF_TOKEN environment variable.")

client = InferenceClient(
    provider="hf-inference",
    api_key=HF_TOKEN,
)

# ----------------------
# Username scoring function (original)
# ----------------------
def username_score(candidate: str) -> int:
    score = 0
    if 3 <= len(candidate) <= 20:
        score += 3
    if re.fullmatch(r"[a-zA-Z0-9_-]+", candidate):
        score += 3
    if not re.search(r"\d{5,}", candidate):  # avoid long numbers
        score += 2
    if candidate.lower() not in ["www", "com", "profile", "in", "linkedin", "github"]:
        score += 2
    return score  # max 10

# ----------------------
# HF Piiranha-v1 scoring
# ----------------------
def piiranha_score(candidate: str) -> float:
    try:
        result = client.token_classification(
            candidate,
            model="iiiorg/piiranha-v1-detect-personal-information"
        )
        # Piiranha returns entities; if it finds a "PERSONAL" entity, assume candidate is likely a real username/name
        score = 0
        for ent in result:
            if ent.get("entity_group") == "PERSONAL":
                score = ent.get("score", 0)
                break
        return score  # 0.0 to 1.0
    except Exception as e:
        print(f"[WARN] Piiranha scoring failed for '{candidate}': {e}")
        return 0.0

# ----------------------
# Paths
# ----------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(script_dir, "osint_results.json")
output_path = os.path.join(script_dir, "filtered_results.json")

# ----------------------
# Load JSON results
# ----------------------
with open(input_path, "r", encoding="utf-8") as f:
    results = json.load(f)

# ----------------------
# Filtering & extracting usernames
# ----------------------
filtered_results = []
SCORE_THRESHOLD = 6  # only update username if combined score >= threshold
PIIRANHA_THRESHOLD = 0.5  # Piiranha score must be at least this

for entry in results:
    url = entry["url"]
    username_candidates = set()

    # Split URL path into segments and subwords
    path = re.sub(r"https?://", "", url).split("/")
    for segment in path:
        for part in re.split(r"[-_.+/]", segment):
            if part:
                username_candidates.add(part)

    # Rate each candidate
    best_username = entry.get("final_username", "")
    best_score = -1
    candidate_best = ""

    for candidate in username_candidates:
        score_human = HumanName(candidate).first != "" or HumanName(candidate).last != ""
        score_username = username_score(candidate)  # 0-10
        score_piiranha = piiranha_score(candidate) * 10  # convert 0-1 to 0-10 scale

        combined_score = (score_human * 5) + score_username + score_piiranha

        if combined_score > best_score:
            best_score = combined_score
            candidate_best = candidate

    # Only update username if combined score and Piiranha score are high enough
    if best_score >= SCORE_THRESHOLD and (piiranha_score(candidate_best) >= PIIRANHA_THRESHOLD):
        best_username = candidate_best

    entry["final_username"] = best_username
    filtered_results.append(entry)

# ----------------------
# Keep top 3 per platform
# ----------------------
top_results = []
platform_groups = {}
for entry in filtered_results:
    platform = entry["platform"]
    platform_groups.setdefault(platform, [])
    platform_groups[platform].append(entry)

for platform, entries in platform_groups.items():
    top_results.extend(entries[:3])  # top 3 now

# ----------------------
# Save filtered results
# ----------------------
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(top_results, f, indent=2)

print(f"Filtered results saved to {output_path}")
