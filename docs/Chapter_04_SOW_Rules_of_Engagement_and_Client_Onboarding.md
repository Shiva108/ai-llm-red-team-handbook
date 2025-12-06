# Chapter 4: SOW, Rules of Engagement, and Client Onboarding

![ ](assets/page_header.svg)

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

_Solid foundations prevent project failure and foster trust. The next chapter will guide you through threat modeling and risk analysis for AI systems, helping you identify what matters most before you begin attacking._
