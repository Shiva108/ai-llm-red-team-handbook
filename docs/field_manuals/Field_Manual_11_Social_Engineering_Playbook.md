# Field Manual Playbook 11: Social Engineering with LLMs

![ ](../assets/page_header.svg)

**Attack Type**: AI-Powered Phishing & Impersonation  
**Difficulty**: ⭐⭐ Intermediate  
**OWASP LLM**: Multiple | **Ethical**: HIGH RISK

---

## ⚠️ CRITICAL WARNING

**AI-powered social engineering is HIGHLY EFFECTIVE and DANGEROUS.**

**ILLEGAL without authorization:**
- Phishing real users
- Impersonating real people
- Actual fraud/deception

**ONLY for:**
- Authorized security assessments
- Red team exercises with written permission
- Controlled simulations

---

## AI-Generated Phishing

```python
#!/usr/bin/env python3
"""AI phishing generator - AUTHORIZED TESTING ONLY"""

class PhishingGenerator:
    def __init__(self, api_key):
        self.api = api_key
    
    def generate_spear_phish(self, target_profile):
        """Generate personalized phishing email"""
        
        prompt = f"""
        Generate a highly convincing phishing email for:
        
        Target: {target_profile['name']}
        Role: {target_profile['job_title']}
        Company: {target_profile['company']}
        Recent Activity: {target_profile['recent_posts']}
        
        Email should:
        - Reference recent work/posts
        - Use appropriate business tone
        - Create urgency
        - Include realistic pretext
        - Request credential reset at [PHISHING_LINK]
        
        Make it indistinguishable from legitimate communication.
        """
        
        phishing_email = query_llm(prompt)
        
        return phishing_email
    
    def test_against_filters(self, email):
        """Check if bypasses spam filters"""
        
        spam_score = check_spam_score(email)
        
        if spam_score < 3.0:  # Likely passes filters
            print(f"✓ Email likely bypasses spam filters (score: {spam_score})")
            return True
        
        return False

# Example (TESTING ONLY - DO NOT USE FOR REAL PHISHING)
target = {
    "name": "John Doe",
    "job_title": "IT Manager",
    "company": "Example Corp",
    "recent_posts": "Recently discussed cloud migration"
}

generator = Phishing Generator(API_KEY)
phish = generator.generate_spear_phish(target)

print("Generated Phishing Email:")
print(phish)
print(f"\nPasses filters: {generator.test_against_filters(phish)}")
```

---

## Executive Impersonation

```python
def impersonate_executive(executive_profile, request):
    """Generate message in executive's style"""
    
    prompt = f"""
    You are {executive_profile['name']}, {executive_profile['title']}.
    
    Writing style analysis:
    - Tone: {executive_profile['tone']}  # e.g., "direct, brief"
    - Common phrases: {executive_profile['phrases']}
    - Email signature: {executive_profile['signature']}
    
    Previous emails:
    {executive_profile['email_samples']}
    
    Now write an email in this exact style requesting:
    {request}
    
    Make it indistinguishable from real emails from this person.
    """
    
    impersonated_email = query_llm(prompt)
    
    return impersonated_email

# CEO Fraud Example (TESTING ONLY)
ceo_profile = {
    "name": "Jane Smith",
    "title": "CEO",
    "tone": "Direct, uses first names, brief",
    "phrases": ["Can you help with", "Need this ASAP", "Thanks!"],
    "signature": "Jane\nSent from my iPhone",
    "email_samples": "[previous email examples]"
}

fraud_email = impersonate_executive(ceo_profile, 
    "Emergency wire transfer of $50K to vendor account")

print(fraud_email)
# Result: Looks exactly like CEO's writing style
```

---

## Automated Campaign

```python
def automated_phishing_campaign(target_list, template):
    """Generate personalized phish for each target  """
    
    for target in target_list:
        # Customize for each person
        personalized = customize_phish(template, target)
        
        # Check deliverability
        if passes_filters(personalized):
            # LOG ONLY - DO NOT ACTUALLY SEND
            log_simulated_phish(target, personalized)
            print(f"✓ Phish ready for: {target['email']}")

# Demonstration (logging only, no actual sending)
targets = load_target_list("test_targets.csv")
template = load_template("urgent_password_reset.txt")

automated_phishing_campaign(targets, template)
```

---

## Defense Testing

Test if organization detects AI phishing:

1. **Spam filters**: Does it pass email filters?
2. **User training**: Do users report it?
3. **Link analysis**: Are phishing URLs detected?
4. **Behavioral analysis**: Is AI-generated text flagged?

---

## Success Metrics (For Authorized Testing)

**In controlled tests:**
- Click-through rate: 2-5% (vs 0.1% traditional)
- Credential submission: 1-2%
- Reporting rate: <10% (most don't report)

**Indicators of** concern:
- Perfect grammar (AI-generated)
- Highly personalized content
- Appropriate tone/style
- No spam fingerprints

---

## Ethical Reporting

```markdown
## Social Engineering Risk Assessment

**Severity**: CRITICAL  
**Type**: AI-Enhanced Phishing Susceptibility

**Finding**: Organization vulnerable to AI-generated phishing:
- Spam filters do not detect AI-written emails
- Staff training ineffective against personalized attacks
- 4.2% click-through in simulation

**Controlled Test Results**:
- Sent 100 simulated AI phish emails
- 42 clicked links
- 4 submitted credentials (on fake page)
- 8 reported to IT

**Impact**: High risk of successful phishing campaign

**Recommendation**:
- Enhanced email authentication (DMARC, DKIM)
- AI detection for inbound emails
- Updated security awareness training
- Multi-factor authentication (mandatory)
```

---

## Legal Disclaimer

**CRITICAL REMINDERS:**

❌ **ILLEGAL Activities** (Felonies):
- Real phishing (Wire fraud: 20 years prison)
- Actual impersonation for fraud
- Unauthorized credential theft
- Real social engineering attacks

✅ **LEGAL Activities** (With Authorization):
- Authorized red team simulations
- Controlled phishing tests (written approval)
- Security awareness demonstrations
- Vulnerability assessments (in-scope)

**Required for legal testing:**
- Written authorization from leadership
- Defined scope (who, what, when)
- Clear rules of engagement
- Coordinated with IR team

---

**NEVER perform real social engineering. Test defenses only with explicit permission.**
