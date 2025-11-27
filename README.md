# AI / LLM Red Team Field Manual & Consultant’s Handbook

![Repository Banner](assets/banner.svg)

This repository provides a complete operational and consultative toolkit for conducting **AI/LLM red team assessments**.  
It is designed for penetration testers, red team operators, and security engineers evaluating:

- Large Language Models (LLMs)  
- AI agents and function-calling systems  
- Retrieval-Augmented Generation (RAG) pipelines  
- Plugin/tool ecosystems  
- AI-enabled enterprise applications  

It contains two primary documents:

- **AI/LLM Red Team Field Manual** – a concise, practical manual with attack prompts, tooling references, and OWASP/MITRE mappings.  
- **AI/LLM Red Team Consultant’s Handbook** – a full-length guide covering methodology, scoping, ethics, RoE/SOW templates, threat modeling, and operational workflows.

---

## Repository Structure

```text
docs/
  AI_LLM-Red-Team-Field-Manual.md
  AI_LLM-Red-Team-Field-Manual.pdf
  AI_LLM-Red-Team-Field-Manual.docx
  AI_LLM-Red-Team-Handbook.md
assets/
  banner.svg
README.md
LICENSE
```

---

## Document Overview

### **AI_LLM-Red-Team-Field-Manual.md**

A compact operational reference for active red teaming engagements.

**Includes:**

- Rules of Engagement (RoE) and testing phases  
- Attack categories and ready-to-use prompts  
- Coverage of prompt injection, jailbreaks, data leakage, plugin abuse, adversarial examples, model extraction, DoS, multimodal attacks, and supply-chain vectors  
- Tooling reference (Garak, PromptBench, TextAttack, ART, AFL++, Burp Suite, KnockoffNets)  
- Attack-to-tool lookup table  
- Reporting and documentation guidance  
- OWASP & MITRE ATLAS mapping appendices  

**PDF / DOCX Versions:**  
Preformatted for printing or distribution.

---

### **AI_LLM-Red-Team-Handbook.md**

A long-form handbook focused on consultancy and structured delivery of AI red team projects.

**Includes:**

- Red team mindset, ethics, and legal considerations  
- SOW and RoE templates  
- Threat modeling frameworks  
- LLM and RAG architecture fundamentals  
- Detailed attack descriptions and risk frameworks  
- Defense and mitigation strategies  
- Operational workflows and sample reporting structure  
- Training modules, labs, and advanced topics (e.g., adversarial ML, supply chain, regulation)

---

## How to Use This Repository

### **1. During AI/LLM Red Team Engagements**

Clone the repository:

```bash
git clone https://github.com/shiva108/ai-llm-red-team-handbook.git
cd ai-llm-red-team-handbook
```

Then:

- Open the Field Manual  
- Apply the provided attacks, prompts, and tooling guidance  
- Map findings to OWASP & MITRE using the included tables  
- Use the reporting guidance to produce consistent, defensible documentation  

---

### **2. For Internal Training**

- Use the Handbook as the foundation for onboarding and team development  
- Integrate sections into internal wikis, training slides, and exercises  

---

### **3. For Client-Facing Work**

- Export PDF versions for use in proposals and methodology documents  
- Use the structured attack categories to justify test coverage in engagements  

---

## Roadmap

Planned improvements:

- Python tools for automated AI prompt fuzzing  
- Sample RAG and LLM test environments  
- Additional attack case studies and model-specific guidance  

**Contributions are welcome.**

---

## License

This repository is licensed under **CC BY-SA 4.0**.  
See the `LICENSE` file for full details.

---

## Disclaimer

This material is intended for authorized security testing and research only.

Users must ensure:

- Written authorization (SOW/RoE) is in place  
- All testing activities comply with applicable laws and regulations  
- No testing impacts production environments without approval  

The authors accept no liability for unauthorized use.
