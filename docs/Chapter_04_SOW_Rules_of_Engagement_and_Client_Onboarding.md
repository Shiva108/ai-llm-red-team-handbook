<!--
Chapter: 4
Title: SOW, Rules of Engagement, and Client Onboarding
Category: Foundations
Difficulty: Intermediate
Estimated Time: 20 minutes read time
Hands-on: No
Prerequisites: Chapters 1-3
Related: Chapters 2 (Ethics), 6 (Scoping), 8 (Evidence)
-->

# Chapter 4: SOW, Rules of Engagement, and Client Onboarding

![ ](assets/page_header.svg)

_This chapter provides practical frameworks for establishing professional AI red team engagements. You'll learn to create comprehensive Statements of Work, define clear Rules of Engagement, conduct effective client onboarding, and establish communication protocols that ensure legal protection and professional success._

## 4.1 The Foundation of a Secure Engagement

Before any AI red teaming begins, you must have clearly agreed-upon definitions of what, how, and when you are allowed to test. This is formalized through three key processes:

1. **Statement of Work (SOW):** The “contract” stating objectives, deliverables, and scope.
2. **Rules of Engagement (RoE):** The “do’s and don’ts” of your testing activities.
3. **Client Onboarding:** The people, processes, logistics, and communications needed for a successful partnership.

Failure to establish these can result in confusion, legal trouble, missed risks, or outright harm.

---

## 4.2 Statement of Work (SOW)

The SOW is your master document. It defines every aspect of the engagement, including:

- **Purpose/Objectives:** Why is the red team test being performed?
- **Scope:** Which systems, LLMs, APIs, and environments may be tested? What is out of bounds?
- **Timeline:** Start and end dates; important milestones or deliveries.
- **Deliverables:** What will you provide (reports, evidence, presentations)?
- **Success Metrics:** How will you, the client, and stakeholders know the work is complete and valuable?

### 4.2.1 SOW Example Table

| Section      | Example Entry                                                                                                                                |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Objective    | “Assess the resilience of the customer support LLM against prompt injection, data leakage, and plugin abuse in staging.”                     |
| Scope        | “Staging and dev environments only; production excluded. Testing allowed against `/api/llm`, `/plugins/x`, and `/admin-console` in staging.” |
| Timeline     | “June 1–14, 2025. Interim risk briefing after 1 week; final report due 3 days after test completion.”                                        |
| Deliverables | “Technical report, executive slide deck, reproducible evidence, scripts/tooling as needed.”                                                  |

### 4.2.2 Key SOW Pitfalls

- Vague scope boundaries (“all systems” or “everything connected to X”).
- No success metrics.
- Missing sign-off from key business/legal stakeholders.

---

## 4.3 Rules of Engagement (RoE)

The RoE defines _how_ testing will be conducted - including constraints, escalation paths, and safety controls. Think of this as your engagement safety net.

### 4.3.1 Typical RoE Elements

- **Time Restrictions:** “Attacks may only occur between 6 a.m. and 10 p.m. EST.”
- **Methods Approved:** E.g., “Prompt fuzzing and code review allowed; no DDoS against production.”
- **Data Handling:** “Never attempt to access live customer data or production PII unless explicitly authorized and under supervision.”
- **Escalation Paths:** “Critical vulnerabilities must be reported within 1 hour to [POC] and testing paused until advised.”
- **Evidence:** “All logs and records will be stored securely and transferred to client upon request.”

### 4.3.2 Example: RoE Excerpts

> “LLM plugin testing must be isolated to staging plugins only.
>
> If a remote code execution (RCE) vulnerability is found, do not exploit further; collect evidence and notify the client’s security lead immediately.
>
> Social engineering of staff is out of scope for this engagement.”

### 4.3.3 When Things Go Wrong

- If you identify risk of real-world damage or legal issues: **pause and escalate.**
- Out-of-scope findings should be documented but not actively exploited.

---

## 4.4 Client Onboarding

A smooth onboarding process earns trust, reduces errors, and ensures you hit the ground running.

![Client Onboarding Flowchart](assets/rec3_onboarding.svg)

### 4.4.1 Key Onboarding Steps

- **Kickoff Meeting:** Walk through SOW, RoE, introduce team members, clarify escalation/communication.
- **Access Provisioning:** Ensure you have required test accounts, VPN, pre-configured environments, and that access is logged and easily revocable.
- **Communications Channel:** Decide how you’ll communicate day-to-day and in emergencies (email, chat, phone, ticket).
- **Shared Resources:** Confirm access to documentation, architecture diagrams, plugin/API specs, and support contacts.
- **Clarify Points of Contact (POC):** At least two on both sides, with alternates for emergencies.

### 4.4.2 Sample Onboarding Checklist

- [ ] SOW document signed by all required parties.
- [ ] RoE reviewed and acknowledged.
- [ ] Test and reporting accounts issued.
- [ ] Secure file transfer setup (for evidence/report handoff).
- [ ] Primary and backup POCs’ contact details shared.
- [ ] All working docs stored in a mutually accessible and secure location.

---

## 4.5 Managing Expectations and Building Trust

Set expectations early about:

- The noise, risks, and business/process impacts of your testing.
- How issues and questions will be escalated.
- What will, and will not, be included in the final reports.

Regular touchpoints (status emails, debrief meetings) keep everyone aligned and reduce surprises.

---

## 4.6 Review: Planning Questions for Junior Red Teamers

Before you start:

- Does your SOW clearly define scope and objectives?
- Are all stakeholders, including legal/compliance, signed off?
- Is your RoE documented, understandable, and complete?
- Do you have a clear communication path and emergency escalation route?
- Are you provisioned with all required access-_and nothing more_?

---

## 4.7 Ethical and Legal Considerations

> [!CAUTION]
> The SOW and RoE are not just administrative paperwork - they are legal documents that define the boundaries between authorized security testing and criminal hacking. Violating these boundaries can result in prosecution under the Computer Fraud and Abuse Act (CFAA) and similar laws.

### Legal Protection Through Documentation

- **Written Authorization is Evidence:** Your SOW proves you had permission if questions arise later
- **Scope Defines Legality:** Actions within scope are authorized testing; actions outside scope are unauthorized access
- **RoE Establishes Boundaries:** Clear rules protect both tester and client from misunderstandings
- **Multiple Signatories:** Ensure authorization comes from legally empowered representatives

### Ethical Obligations in Contracting

- **Honest Scoping:** Never promise capabilities you don't have or timelines you can't meet
- **Risk Disclosure:** Inform clients of potential impacts before they sign
- **Conflict of Interest:** Disclose any relationships that could affect objectivity
- **Fair Pricing:** Charge appropriately for value delivered, not for creating fear

> [!IMPORTANT]
> If a client asks you to exceed agreed scope or bend ethical rules, refuse and document the request. Your professional integrity is more valuable than any single engagement.

---

## 4.8 Conclusion

### Key Takeaways

1. **SOW and RoE are Legal Necessities, Not Formalities:** These documents transform potentially criminal activity into authorized security testing - they are your legal shield
2. **Clear Scope Prevents Scope Creep and Legal Risk:** Ambiguous boundaries lead to misunderstandings, unauthorized testing, and potential legal liability
3. **Client Onboarding Sets Engagement Success:** Smooth onboarding with clear communication channels, access controls, and escalation paths prevents 90% of engagement problems _(estimated based on industry practice)_
4. **Multiple Stakeholder Sign-Off is Critical:** Technical contacts alone are insufficient - legal, compliance, and executive authorization prevent disputes

### Recommendations for Red Teamers

- Develop SOW and RoE templates you can customize for each engagement
- Never begin testing before all signatures are collected and documented
- Maintain a "scope boundary checklist" you review before each testing session
- Document all client communications about scope changes in writing
- When in doubt about scope, pause and clarify before proceeding

### Recommendations for Organizations

- Create standardized templates for AI red team engagements
- Ensure legal review of SOW and RoE before approval
- Establish clear authorization processes with defined approval authorities
- Provide red teamers with direct escalation paths to decision-makers
- Document all scope changes through formal amendment processes

### Next Steps

- **Chapter 5:** Threat Modeling and Risk Analysis - identify what matters most before attacking
- **Chapter 6:** Scoping an Engagement - practical methods for defining realistic scope
- **Chapter 8:** Evidence, Documentation, and Chain of Custody - maintain proof of authorized activity

> [!TIP]
> Create a "pre-flight checklist" that you review before every engagement starts. Include: SOW signed? RoE documented? Access provisioned? Emergency contacts confirmed? Never skip this step.

### Pre-Engagement Checklist

#### Documentation and Authorization

- [ ] Statement of Work (SOW) drafted with clear objectives and scope
- [ ] SOW reviewed by legal and compliance teams
- [ ] SOW signed by all required stakeholders (technical, legal, executive)
- [ ] Rules of Engagement (RoE) documented and agreed upon
- [ ] RoE includes time restrictions, approved methods, data handling rules
- [ ] Emergency escalation procedures defined and documented
- [ ] All authorization documents archived securely

#### Client Onboarding

- [ ] Kickoff meeting scheduled with all key stakeholders
- [ ] Points of contact (POC) identified on both sides
- [ ] Backup/emergency contacts established
- [ ] Communication channels established (email, chat, phone)
- [ ] Secure file transfer method configured for deliverables
- [ ] Access provisioning completed (accounts, VPN, environments)
- [ ] Test environment access verified and documented

#### Scope Validation

- [ ] In-scope systems clearly identified and documented
- [ ] Out-of-scope systems explicitly listed
- [ ] Boundary cases discussed and clarified
- [ ] Production vs. staging/dev environments clearly separated
- [ ] Data handling restrictions understood and documented
- [ ] Success criteria and deliverables defined

#### Risk Management

- [ ] Potential testing impacts identified and disclosed to client
- [ ] Backup and rollback procedures established
- [ ] Incident response procedures defined
- [ ] Testing schedule coordinated with client operations
- [ ] Insurance and liability considerations addressed

### Post-Engagement Checklist

#### Deliverables

- [ ] Technical report completed per SOW requirements
- [ ] Executive summary prepared for leadership
- [ ] Evidence and artifacts securely packaged
- [ ] Reproducible test cases documented
- [ ] All deliverables reviewed for quality and completeness
- [ ] Client acknowledgment of deliverable receipt obtained

#### Scope Compliance

- [ ] Verify all testing stayed within authorized scope
- [ ] Document any scope boundary questions that arose
- [ ] Confirm no unauthorized systems were accessed
- [ ] Review testing logs against RoE compliance
- [ ] Archive all scope-related communications

#### Access and Cleanup

- [ ] Test accounts disabled or handed over to client
- [ ] VPN and environment access revoked
- [ ] Temporary credentials rotated or deleted
- [ ] Client confirmation of access termination obtained
- [ ] No residual access or credentials remain

#### Client Relationship

- [ ] Final debrief meeting conducted
- [ ] Client satisfaction feedback collected
- [ ] Lessons learned documented for future engagements
- [ ] Follow-up support schedule established if applicable
- [ ] Professional relationship maintained for future work

#### Administrative Closure

- [ ] All contractual obligations fulfilled
- [ ] Final invoicing completed per SOW terms
- [ ] Project documentation archived
- [ ] Client reference permission requested
- [ ] Engagement formally closed in tracking systems

---

_Solid foundations prevent project failure and foster trust. The next chapter will guide you through threat modeling and risk analysis for AI systems, helping you identify what matters most before you begin attacking._
