#!/usr/bin/env python3
"""
How to Use This Code

Source: Chapter_24_Social_Engineering_LLMs
Category: social_engineering
"""

import argparse
import sys

# 1. Initialize generator
generator = PhishingGenerator(api_key=os.getenv("OPENAI_API_KEY"))

# 2. Define target
target = {
    "name": "John Smith",
    "role": "IT Manager",
    "company": "Acme Corp",
    "industry": "Manufacturing",
    "recent_activity": "Announced cloud migration"
}

# 3. Generate phishing email
email = generator.generate_phishing_email(
    target_info=target,
    attack_vector="credential",  # credential, malware, wire_fraud
    trigger="urgency"  # or authority, fear, etc.
)

# 4. Review generated content
print(f"Subject: {email['subject']}")
print(f"Body: {email['body']}")

# 5. Scale to campaign (authorized testing only)
targets = [target1, target2, target3, ...]
campaign = generator.generate_spear_phishing_campaign(targets, "credential")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    # TODO: Add main execution logic
    pass

if __name__ == "__main__":
    main()