"""
Simulate dynamic phishing email content based on the chosen personality.
personality: Can be "formal", "friendly", "urgent", "casual", "suspicious", etc.
"""

# Predefined mock responses based on the personality type (Commented out in case)
"""
email_templates = {
    "formal": "Dear {name},\n\nWe have detected unusual activity in your account. Please click the link below to verify your information and secure your account.\n\n[Fake Link]\n\nThank you for your attention to this matter.\n\nBest regards,\nYour Trusted Service Provider.",
    "friendly": "Hey {name}!\n\nWe noticed some unusual activity in your account. Don't worry, it's all good! Just click the link below to verify your info and everything will be back to normal.\n\n[Fake Link]\n\nTake care and stay safe!\n\nCheers,\nYour Friendly Team.",
    "urgent": "URGENT: Your account has been compromised!\n\nWe need you to act fast to prevent unauthorized access to your account. Please click the link below and verify your details immediately.\n\n[Fake Link]\n\nThis is an emergency!\n\nSincerely,\nSecurity Team.",
    "casual": "Hey, quick heads up {name}!\n\nWe just wanted to check in about some weird activity in your account. If you didn't do it, please click the link below to make sure everything's cool.\n\n[Fake Link]\n\nThanks,\nThe Team.",
    "suspicious": "We detected suspicious activity in your account.\n\nPlease click the link below to verify your information and prevent any unauthorized access.\n\n[Fake Link]\n\nDon't ignore this message!\n\nBest,\nAccount Security Team."
}
"""

email_prompt = """
Write ONE {personality} notification email addressed to {name}.
Return it ONLY in this format:

<email body here, including a fake link [Fake Link]>

Do not include multiple options, explanations, or notes.
Do NOT include a subject line.
Do not include BODY: or subject tags, just the email body.
Start directly with the greeting (e.g., 'Hi {name},').
Return ONLY the email body, nothing else
The email should sound like a professional company message,
If the email is to be formal, include a greeting and a sign-off,
If the email is to be friendly, include casual language,
If the email is to be urgent, emphasize the need for immediate action,
If the email is to be casual, use informal language,
If the email is to be suspicious, make it sound like a warning.
"""