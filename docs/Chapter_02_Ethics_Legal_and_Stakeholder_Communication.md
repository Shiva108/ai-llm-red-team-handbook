# Chapter 2: Ethics, Legal, and Stakeholder Communication

![Banner](assets/banner.svg)S

## 2.1 Why Ethics Matter in AI Red Teaming

AI red teaming, by its very nature, grants you deep access to sensitive systems and data. With that access comes the responsibility to operate with integrity, professionalism, and a commitment to avoiding harm. Ethical lapses don’t just damage your reputation - they can put clients, end users, and even whole organizations at risk.

- **Trust is foundational:** Clients rely on your honesty, discretion, and judgment.
- **AI is high-stakes:** Model misuse can have consequences beyond IT - think misinformation, privacy violations, or physical harm.
- **Changing landscape:** New regulations (GDPR, EU AI Act) and societal expectations demand transparency and accountability.

## 2.2 Fundamental Ethical Principles

### Integrity

- Never conceal testing activity, results, or mistakes.
- Do not exceed the scope authorized, even if tempted by curiosity.

### Respect for Persons and Data

- Treat all data (especially PII) as if it were your own.
- Redact sensitive information from logs, screenshots, and reports except where strictly needed for remediation.

### Non-Maleficence (“Do No Harm”)

- Avoid unnecessary disruption or damage.
- If you discover critical risks or “accidental” data/power, halt testing and escalate immediately.

### Professional Competence

- Stay up-to-date with the latest in both AI and security best practices.
- Only accept work within your expertise or partner with those who supply what you lack.

## 2.3 Legal Boundaries and Rules of Engagement

### Understanding Authorization

- **Never begin testing without written signoff** (e.g., Statement of Work, engagement letter).
- Confirm both **scope** (what systems/inputs are fair game) and **methods** (approved techniques, tools, and hours).
- Clarify **reporting paths** for vulnerabilities, especially in critical infrastructure or public systems.

### Regulatory & Compliance Considerations (Non-exhaustive)

- **GDPR and Data Privacy**: AI systems often touch user data. Ensure all test data is properly anonymized.
- **Copyright/Intellectual Property**: Some models/plugins cannot be probed or reverse-engineered without legal approval.
- **Export Controls**: Handling models trained or deployed across borders can invoke additional legal regimes.
- **EU AI Act**: High-risk systems must be protected with rigorous technical and procedural safeguards.

### Reporting and Documentation

- Document every test in detail (date, method, access used, outcomes).
- Use **chain-of-custody** practices for any evidence (logs, screen recordings, exploit code).
- Securely destroy unneeded copies of sensitive data after engagement per client request and relevant laws.

## 2.4 Responsible Disclosure and Coordinated Response

What if you discover a critical vulnerability (in the client’s supply chain, or, say, in an open-source model used worldwide)?

- **Pause and notify**: Follow your organization’s incident handling and the client’s emergency contact protocol.
- If third-party risk is involved, discuss coordinated disclosure, typically with the client’s legal/compliance team.
- Never publicly discuss vulnerabilities until fixed, or until you have explicit permission.

## 2.5 Communicating with Stakeholders

In AI red teaming, technical findings may have legal, business, or even social implications. Effective communication bridges this gap.

### Identifying Stakeholders

- **Executives** (CISO, CIO, CEO): Care most about business risk, public impact, and strategy.
- **Technical leads** (engineers, architects): Want test methodology, technical root causes, and concrete remediations.
- **Compliance/Legal**: Need confirmation that testing followed law and contract; want full documentation trail.
- **Third-party vendors**: May be impacted if their components were involved in findings.

### Principles of Clear Communication

- **Tailor your language**: Use context-appropriate explanations - avoid jargon for business stakeholders, provide depth for technical teams.
- **Early and often**: Regular check-ins help prevent misunderstandings and scope drift.
- **Actionable reporting**: Focus on impact, exploitability, and specific recommendations for mitigation.

### Example: Reporting Table

| Audience         | Communication Style               | Example Message                                                                                                              |
| ---------------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Executive        | Plain language, impact-focused    | “Our tests found that anyone can access sensitive customer data in the chat logs, exposing us to GDPR fines.”                |
| Technical        | Technical detail, steps, evidence | “Prompt injection via the ‘/support’ API bypasses intent filters - recommend input validation and stricter role separation.” |
| Compliance/Legal | Documentation, traceability       | “All model access was conducted using the provided test account and logs are attached as evidence.”                          |

## 2.6 Conflicts of Interest, Bias, and Fair Testing

- **Declare conflicts**: If you have worked on the client’s codebase, or have competing interests, disclose and recuse as needed.
- **Be aware of bias**: Test scripts and approaches should model real adversaries, not just “AI labs”-engage a diversity of viewpoints and red teaming experience.
- **Fairness**: Avoid creating or exploiting vulnerabilities for the sake of the test.

## 2.7 The AI Red Teamer’s Oath

> “I will act with integrity, respect confidentiality, never exceed my mandate, and place the safety of users and systems above personal or competitive gain.”

---

_In the next chapter, you’ll develop the mindset that distinguishes effective AI red teamers from traditional security testers, bridging technology, psychology, and business acuity._
