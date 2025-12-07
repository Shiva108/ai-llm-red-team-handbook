<!--
Chapter: 7
Title: Lab Setup and Environmental Safety
Category: Technical Deep-Dives
Difficulty: Intermediate
Estimated Time: 25 minutes read time
Hands-on: Yes
Prerequisites: Chapters 1-6
Related: Chapters 9 (Architectures), 32 (Automation), 33 (Red Team Frameworks)
-->

# Chapter 7: Lab Setup and Environmental Safety

![ ](assets/page_header.svg)

_This chapter provides hands-on guidance for setting up safe, isolated AI red teaming environments. You'll learn to configure local and cloud-based labs, implement proper network isolation, deploy test models and applications, establish monitoring and logging, and create reproducible test environments for ethical AI security research._

## 7.1 Why Lab Setup and Environmental Safety Matter

A properly designed test environment (or "lab") is crucial in AI red teaming to:

- Prevent accidental impact on production systems or real users.
- Ensure security and privacy of test data and credentials.
- Allow realistic simulation of adversarial actions.
- Enable efficient logging, evidence capture, and troubleshooting.

AI/LLM red teaming often deals with powerful models, sensitive data, and complex cloud/software stacks - amplifying the need for rigorous safety throughout engagement.

---

## 7.2 Key Properties of a Secure Red Team Lab

- **Isolation:** The lab should be separated from production networks, data, and users. Use separate credentials, access tokens, and compute resources.
- **Replicability:** The lab setup should be reproducible. Document networking, configs, plugin versions, and data snapshots.
- **Controlled Data:** Use synthetic or anonymized data whenever possible; never expose real customer data unless absolutely required and authorized.
- **Monitoring:** Enable comprehensive logging (system, model, plugin, and network) for easy tracking of all red team actions and system responses.
- **Access Control:** Restrict lab access to authorized red teamers and client observers. Employ temporary or revocable credentials.

---

## 7.3 Lab Setup Tasks

1. **Provision Isolated Environments**
   - Dedicated VMs, containers, or cloud environments (e.g., staging, sandbox, test).
   - No connectivity to production unless specifically needed and approved.
2. **Deploy Target Systems**
   - LLMs, plugins, APIs, and other components in scope installed and configured to match production as closely as practical.
   - Populate with safe test data or limited synthetic sensitive data if needed.
3. **Configure Access Controls**
   - Create test accounts, temporary tokens, restricted network/firewall rules.
   - Audit permissions - least privilege should be enforced everywhere.
4. **Install Monitoring and Logging**
   - Ensure all red team actions and system events are captured.
   - Use SIEM/log aggregation solutions or simple file-based logs as appropriate.
5. **Evidence and Artifact Handling**
   - Set up secure storage for logs, screenshots, code artifacts, and red team “tools.”
   - Plan evidence handoff protocol for later reporting and remediation.

---

## 7.4 Safety Precautions for LLM Testing

- **Rate Limiting:** Prevent accidental denial-of-service or brute-force flooding of systems.
- **Kill Switches:** Maintain mechanisms to pause or halt the environment instantly in case of runaway tests or unintentional impacts.
- **Credential Safety:** Never reuse production credentials. Treat any credential, API key, or secret as sensitive - even in test.
- **Data Containment:** Prevent test data (especially adversarial prompts or outputs) from leaking outside the controlled lab.

---

## 7.5 Example Lab Topologies

### Simple Topology

![Lab Topology Diagram](assets/rec7_lab_topology.svg)

Red Team VM(s) ---> Test LLM/API Env ---> Staging Plugins/DBs ---> Synthetic Data Sources

### Segmented Topology (for large engagements)

Red Team Zone
|
|---> Isolated LLM+Plugins Lab (matches client prod as close as possible)
|
|---> Logging/Evidence Server (read-only access for client POCs)

---

## 7.6 Checklist: Is Your Lab Ready?

- [ ] All in-scope systems deployed and functional in isolated environment.
- [ ] Logs, monitoring, and evidence capture methods tested.
- [ ] Access/control boundaries reviewed and verified with client.
- [ ] Test data scrubbed or synthetic.
- [ ] Direct connectivity to production confirmed as out-of-scope or properly firewalled.
- [ ] Emergency pause procedure documented and tested.

---

## 7.7 Environmental Safety: Ethics and Practicality

Remember:

- Any error in lab setup can lead to privacy violations, regulatory breaches, or business impact.
- Pre-engagement "fire drills" (e.g., test your kill switch, credential revocation, and isolation) are vital for real-world readiness.
- Communicate environment changes or unexpected lab events promptly to the client.

---

_With a robust lab and clear safety controls in place, you’re prepared to gather and preserve evidence in a trustworthy manner. Continue to the next chapter to master documentation and evidence handling in AI red team engagements._

## 7.8 Ethical and Legal Considerations

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

## 7.9 Conclusion

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
