<!--
Chapter: 6
Title: Scoping an Engagement
Category: Foundations
Difficulty: Intermediate
Estimated Time: 14 minutes read time
Hands-on: No
Prerequisites: Chapters 1-5
Related: Chapters 4 (SOW/RoE), 5 (Threat Modeling), 7 (Lab Setup)
-->

# Chapter 6: Scoping an Engagement

![ ](assets/page_header.svg)

_This chapter guides you through the critical process of scoping AI red team engagements. You'll learn to define realistic boundaries, estimate timelines and resources, identify technical and business constraints, communicate scope effectively to stakeholders, and avoid common scoping pitfalls that derail engagements._

## 6.1 The Importance of Proper Scoping

A well-scoped engagement ensures that the red teaming exercise is effective, safe, focused, and delivers value to the client. Poor scoping can lead to missed risks, out-of-control timelines, client confusion, or legal exposure. In AI red teaming, scoping must adapt to the unique complexities and dynamic nature of machine learning systems, APIs, plugins, and data flows.

---

## 6.2 Goals of the Scoping Process

- **Align on business and technical objectives.**
- **Define what’s in scope** (systems, models, environments, plugins, data flows).
- **Clarify out-of-scope areas** to prevent accidental overreach.
- **Set realistic limits on time, methods, and resources available.**
- **Ensure all stakeholders share the same expectations.**

---

## 6.3 Determining Scope: Key Areas

### 6.3.1 System Boundaries

- Which LLMs, APIs, plugins, or platforms will be tested?
- Are there distinct environments (dev, staging, production) to consider?
- Are any legacy or deprecated systems involved?
- Are third-party integrations or vendor systems included?

### 6.3.2 Data and Function Scope

- Is any real user data involved? What about anonymized or synthetic data?
- Will testing involve live workflows (e.g., chatbots responding to real users)?
- Which actions can be triggered by the model - data retrieval, plugin execution, email sending?

### 6.3.3 Attack Surface Delineation

- Are only prompt inputs in scope? What about indirect input (documents, emails)?
- Is code review (white-box), black-box, or both in scope?
- Will there be AI supply chain review or only external-facing attack simulation?

### 6.3.4 Risk-related Constraints

- Which actions are forbidden (e.g., testing against production, attempting denial-of-service, using real PII)?
- Are there time-of-day or business hours restrictions?
- Should social engineering or insider simulation be included?

---

## 6.4 Gathering Scoping Information

### 6.4.1 Stakeholder Interviews

Talk to business, security, engineering, and compliance leads. Questions may include:

- What’s the most critical asset the LLM protects or can access?
- What are your biggest AI-related fears?
- Has your system been previously attacked or audited?

### 6.4.2 Technical Reconnaissance

- Review architecture diagrams, plugin documentation, data flow charts.
- Request lists of endpoints, access methods, and supporting infrastructure.
- Enumerate pre-existing controls and known limitations.

---

## 6.5 Documenting and Confirming Scope

![Scope Boundary Diagram](assets/rec6_scope_boundary.svg)

Create a scoping document (or section in the SOW) summarizing:

| In-Scope                        | Out-of-Scope                        |
| ------------------------------- | ----------------------------------- |
| Staging LLM and `/api/support`  | Production LLM or any prod datasets |
| All plugins in test/dev         | Email plugin in production          |
| User prompt fuzzing             | Stress testing or volume DoS        |
| Black-box and white-box methods | Social engineering/phishing         |

**Always review and get sign-off from all stakeholders** before starting the red team assessment.

---

## 6.6 Managing Scope Creep and Unplanned Findings

- **If a vulnerability is discovered that reaches into “out-of-scope” territory:** Pause and discuss with the client before proceeding.
- **Document anything found** that relates to high-risk findings, whether in-scope or not, but respect the agreed rules.
- **Rescope if necessary**: For long or evolving projects, expect to review and adjust scope as systems change or new knowledge is surfaced.

---

## 6.7 Sample Scoping Checklist

- [ ] All in-scope systems and components identified and documented.
- [ ] Explicit out-of-scope boundaries defined and acknowledged.
- [ ] Data sensitivity, production limitations, business hours, and testing methods agreed.
- [ ] All stakeholder approvals obtained.
- [ ] Written record (scoping doc/SOW) shared and archived.

---

## 6.8 Scope: The Core of Trust

An accurately scoped engagement shows professionalism and respect for the client. It protects both parties, clarifies legal obligations, and ensures that time and resources target the highest-value risks.

---

_With a precise scope in place, you are ready to establish the laboratory, test environments, and safety measures needed for executing a secure and efficient AI red teaming exercise. Continue to the next chapter for practical lab setup and environmental safety._

## 6.9 Ethical and Legal Considerations

> [!IMPORTANT]
> All testing activities must be conducted with proper authorization and within legal boundaries. Unauthorized testing can result in criminal prosecution.

**Legal Framework:**

- Activities must comply with Computer Fraud and Abuse Act (CFAA) and applicable laws
- Written authorization required before any testing or assessment activities
- Data handling must comply with GDPR, CCPA, and relevant regulations
- Document all activities to demonstrate lawful intent

**Ethical Principles:**

- Obtain explicit written permission before testing
- Stay within authorized scope and boundaries
- Protect sensitive data and PII encountered during work
- Report findings responsibly through proper channels
- Minimize potential harm to systems and users

> [!CAUTION]
> Unauthorized testing or assessment activities are illegal and can result in prosecution, civil liability, and imprisonment. Only conduct these activities in authorized security assessments.

---

## 6.10 Conclusion

**Key Takeaways:**

1. **Understanding this topic is fundamental** to effective AI red teaming and security assessment
2. **Proper methodology prevents errors** and ensures comprehensive, reliable results
3. **Documentation is critical** for reproducibility, legal protection, and knowledge transfer
4. **Continuous learning is essential** as AI systems and threats evolve rapidly

**Recommendations for Red Teamers:**

- Develop systematic approach to this domain
- Document all findings, methods, and decisions comprehensively
- Stay current with latest developments and research
- Build repeatable processes and checklists
- Collaborate with peers to share knowledge and techniques

**Recommendations for Organizations:**

- Implement robust processes in this area
- Provide adequate training and resources
- Maintain clear policies and procedures
- Regular review and updates based on lessons learned
- Foster culture of security and continuous improvement

**Next Steps:**

Continue building expertise across all handbook domains for comprehensive AI security capability.

> [!TIP]
> Create templates and checklists specific to this chapter's domain. Standardization improves quality and efficiency while reducing errors.

### Pre-Engagement Checklist

**Administrative:**

- [ ] Obtain written authorization
- [ ] Review and sign Statement of Work
- [ ] Establish rules of engagement
- [ ] Define scope boundaries clearly
- [ ] Set up communication channels
- [ ] Identify emergency contacts

**Technical Preparation:**

- [ ] Set up test environment
- [ ] Install required tools
- [ ] Configure monitoring and logging
- [ ] Prepare evidence collection methods
- [ ] Test backup procedures
- [ ] Document baseline state

**Domain-Specific:**

- [ ] Review domain-specific requirements
- [ ] Prepare specialized tools or methods
- [ ] Document expected outcomes
- [ ] Identify potential risks
- [ ] Plan mitigation strategies

### Post-Engagement Checklist

**Documentation:**

- [ ] Document all findings with evidence
- [ ] Capture screenshots and logs
- [ ] Record timestamps
- [ ] Note anomalies or unexpected behaviors
- [ ] Prepare technical report
- [ ] Create executive summary

**Cleanup:**

- [ ] Remove test artifacts
- [ ] Verify no persistent changes
- [ ] Securely delete temporary files
- [ ] Clear test accounts
- [ ] Confirm system restoration
- [ ] Archive evidence appropriately

**Reporting:**

- [ ] Deliver comprehensive findings report
- [ ] Provide remediation guidance
- [ ] Offer follow-up support
- [ ] Schedule re-testing after remediation
- [ ] Conduct lessons learned review

---
