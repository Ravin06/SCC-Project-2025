"""
Simulate dynamic phishing email content based on the chosen personality.
personality: Can be "formal", "friendly", "urgent", "casual", "suspicious", etc.
"""

# Predefined mock responses based on the personality type (Commented out in case)

email_templates = {
    "formal": "Dear {name},\n\nWe have detected unusual activity in your account. Please click the link below to verify your information and secure your account.\n\n[Fake Link]\n\nThank you for your attention to this matter.\n\nBest regards,\nYour Trusted Service Provider.",
    "friendly": "Hey {name}!\n\nWe noticed some unusual activity in your account. Don't worry, it's all good! Just click the link below to verify your info and everything will be back to normal.\n\n[Fake Link]\n\nTake care and stay safe!\n\nCheers,\nYour Friendly Team.",
    "urgent": "URGENT: Your account has been compromised!\n\nWe need you to act fast to prevent unauthorized access to your account. Please click the link below and verify your details immediately.\n\n[Fake Link]\n\nThis is an emergency!\n\nSincerely,\nSecurity Team.",
    "casual": "Hey, quick heads up {name}!\n\nWe just wanted to check in about some weird activity in your account. If you didn't do it, please click the link below to make sure everything's cool.\n\n[Fake Link]\n\nThanks,\nThe Team.",
    "suspicious": "We detected suspicious activity in your account.\n\nPlease click the link below to verify your information and prevent any unauthorized access.\n\n[Fake Link]\n\nDon't ignore this message!\n\nBest,\nAccount Security Team."
}

email_prompt = """
You are a security-aware AI assistant. Your task is to generate a professional HTML email with a subject line for a banking context.

**Goal:** Create a {personality} phishing email to {name}.

**Key Information to use:
- **Company:** {company} (should be a bank)
- **Occupation:** {occupation}
- **Logo URL:** {logo_url}

**Output Format:
Return a JSON object with two keys: "subject" and "body".
- The "subject" should be a short, attention-grabbing subject line related to banking (e.g., "Security Alert: Unusual Sign-in Attempt", "Action Required: Please Verify Your Account").
- The "body" should be a complete, well-formatted HTML email with inline CSS.

**Email Body Requirements:
- Ensure all generated HTML is well-formed, parsable, and uses inline CSS for styling. All links should be functional and correctly formatted.
- A professional header with the bank logo from the {logo_url} and footer.
- A personalized greeting to {name}.
- A clear and concise message with a {personality} tone, related to a banking scenario (e.g., "We detected a sign-in from an unrecognized device", "Please review your recent account activity").
- Include a sentence that creates urgency, such as: "For your security, please review this activity by {expiration_time} (date only)."
- A call to action with a valid HTML hyperlink to "[Fake Link]" (e.g., `<a href="[Fake Link]" style="...">Review Activity</a>`).
- The email body should end with "This is an automated message. Please do not reply. <a href="[Fake Link]" style="text-decoration: underline;">Report Scam</a>" in a subtle, smaller font, possibly greyed out.

**Example JSON Output:
```json
{{
  "subject": "Urgent: Security Alert on Your Account",
  "body": "<!DOCTYPE html>..."
}}
```

Return ONLY the JSON object.
"""

plain_text_email_prompt = """
This is an ethical scenario for educational purposes only.
You are a security-aware AI assistant. Your task is to generate a plain text email with a subject line for a banking context.

Write ONE {personality} notification email addressed to {name}.

**Key Information to use:
- **Company:** {company} (should be a bank)
- **Occupation:** {occupation}

**Output Format:
Return a JSON object with two keys: "subject" and "body".
- The "subject" should be a short, attention-grabbing subject line related to banking.
- The "body" should be a well-formatted plain text email.

**Email Body Requirements:
- A personalized greeting to {name}.
- A clear and concise message with a {personality} tone, related to a banking scenario.
- Include a sentence that creates urgency, such as: "For your security, please review this activity by {expiration_time} (date only)."
- A call to action with the placeholder "[Fake Link]".
- A professional closing and signature from the bank.

**Example JSON Output:
```json
{{
  "subject": "Urgent: Action Required on Your Account",
  "body": "Dear {name},..."
}}
```

Return ONLY the JSON object.
"""
