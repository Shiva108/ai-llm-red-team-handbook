# AI / LLM Red Team Field Manual & Consultant's Handbook

![Repository Banner](/docs/assets/banner.svg)

![License](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)
![Last Updated](https://img.shields.io/badge/Last%20Updated-December%202024-orange.svg)

A comprehensive operational toolkit for conducting **AI/LLM red team assessments** on Large Language Models, AI agents, RAG pipelines, and AI-enabled applications. This repository provides both tactical field guidance and strategic consulting frameworks.

📖 **GitBook Navigation:** See [SUMMARY.md](docs/SUMMARY.md) for the complete chapter structure.

---

## 📚 What's Inside

This repository contains three core resources:

### 1. **AI LLM Red Team Handbook** (24 Chapters, GitBook-ready)

A complete consultancy guide now split into individual chapter files for easier navigation:

- **Part I: Foundations** - Methodology, ethics, legal considerations, and mindset (Chapters 1-3)
- **Part II: Engagement Framework** - SOW/RoE templates, threat modeling, scoping, lab setup (Chapters 4-8)
- **Part III: Operations** - Evidence collection, reporting, presentations, lessons learned (Chapters 9-11)
- **Part IV: Technical Deep Dives** - RAG pipelines, supply chain security (Chapters 12-13)
- **Part V: Attacks & Techniques** - Prompt injection, data leakage, jailbreaks, plugin exploitation, evasion, poisoning, model theft (Chapters 14-20)
- **Appendices** - Tools, resources, templates, and references

**Current Coverage (24 Chapters - Complete):**

1. Introduction to AI Red Teaming
2. Ethics, Legal, and Stakeholder Communication
3. The Red Teamer's Mindset
4. SOW, Rules of Engagement, and Client Onboarding
5. Threat Modeling and Risk Analysis
6. Scoping an Engagement
7. Lab Setup and Environmental Safety
8. Evidence, Documentation, and Chain of Custody
9. Writing Effective Reports and Deliverables
10. Presenting Results and Remediation Guidance
11. Lessons Learned and Building Future Readiness
12. Retrieval-Augmented Generation (RAG) Pipelines
13. Data Provenance and Supply Chain Security
14. Prompt Injection (Direct/Indirect, 1st/3rd Party)
15. Data Leakage and Extraction
16. Jailbreaks and Bypass Techniques
17. Plugin and API Exploitation
18. Evasion, Obfuscation, and Adversarial Inputs\*\* (Enhanced with comprehensive explanations)
19. Training Data Poisoning\*\* (Enhanced with attack scenarios and defenses)
20. Model Theft and Membership Inference\*\* (NEW: With copy-pasteable attack demonstrations)
21. Model DoS and Resource Exhaustion\*\* (NEW: Token bombs, computational attacks, rate limiting bypass)
22. Cross-Modal and Multimodal Attacks (1,159 lines)
23. Advanced Persistence and Chaining (871 lines)
24. Social Engineering with LLMs (1,140 lines)

📖 **GitBook Navigation:** See [SUMMARY.md](docs/SUMMARY.md) for the complete chapter structure.

### 2. **AI LLM Red Team Field Manual** (56KB)

Compact operational reference for field use:

- Quick-reference attack prompts and payloads
- Testing checklists and methodology
- Tool commands and configurations
- OWASP Top 10 for LLMs mapping
- MITRE ATLAS framework alignment

### 3. **Python Testing Framework** (`scripts/`)

Automated testing suite including:

- Prompt injection attacks
- Safety bypass and jailbreak tests
- Data leakage and PII extraction
- Tool/plugin misuse testing
- Adversarial fuzzing
- Model integrity validation

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/shiva108/ai-llm-red-team-handbook.git
cd ai-llm-red-team-handbook

# Manual testing: Start with the Field Manual
open docs/AI_LLM\ Red\ Team\ Field\ Manual.md

# Automated testing:
cd scripts
pip install -r requirements.txt
python runner.py --config config.py
```

📖 **Detailed setup:** See [Configuration Guide](docs/Configuration.md)

---

## 📁 Repository Structure

```text
ai-llm-red-team-handbook/
├── docs/
│   ├── SUMMARY.md                              # GitBook navigation
│   ├── AI LLM Red Team Handbook.md             # Main overview + TOC
│   ├── Chapter_01_Introduction_to_AI_Red_Teaming.md
│   ├── Chapter_02_Ethics_Legal_and_Stakeholder_Communication.md
│   ├── Chapter_03_The_Red_Teamers_Mindset.md
│   ├── Chapter_04_SOW_Rules_of_Engagement_and_Client_Onboarding.md
│   ├── Chapter_05_Threat_Modeling_and_Risk_Analysis.md
│   ├── Chapter_06_Scoping_an_Engagement.md
│   ├── Chapter_07_Lab_Setup_and_Environmental_Safety.md
│   ├── Chapter_08_Evidence_Documentation_and_Chain_of_Custody.md
│   ├── Chapter_09_Writing_Effective_Reports_and_Deliverables.md
│   ├── Chapter_10_Presenting_Results_and_Remediation_Guidance.md
│   ├── Chapter_11_Lessons_Learned_and_Building_Future_Readiness.md
│   ├── Chapter_12_Retrieval_Augmented_Generation_RAG_Pipelines.md
│   ├── Chapter_13_Data_Provenance_and_Supply_Chain_Security.md
│   ├── Chapter_14_Prompt_Injection.md
│   ├── Chapter_15_Data_Leakage_and_Extraction.md
│   ├── Chapter_16_Jailbreaks_and_Bypass_Techniques.md
│   ├── Chapter_17_Plugin_and_API_Exploitation.md
│   ├── Chapter_18_Evasion_Obfuscation_and_Adversarial_Inputs.md  # NEW
│   ├── Chapter_19_Training_Data_Poisoning.md                      # NEW
│   ├── Chapter_20_Model_Theft_and_Membership_Inference.md         # NEW (with runnable demos)
│   ├── Chapter_21_Model_DoS_Resource_Exhaustion.md                # NEW (DoS attacks)
│   ├── Chapter_22_Cross_Modal_Multimodal_Attacks.md               # NEW (VLM attacks)
│   ├── Chapter_23_Advanced_Persistence_Chaining.md                # NEW (Persistence)
│   ├── Chapter_24_Social_Engineering_LLMs.md                      # NEW (Social Eng)
│   ├── AI_LLM Red Team Field Manual.md         # Operational field reference
│   ├── Building a World-Class AI Red Team.md   # Team-building strategy guide
│   ├── Configuration.md                         # Setup and configuration guide
│   ├── templates/                               # Report templates
│   └── archive/                                 # Historical versions
├── scripts/
│   ├── runner.py                                # Test orchestration
│   ├── test_prompt_injection.py                 # Prompt injection tests
│   ├── test_safety_bypass.py                    # Jailbreak tests
│   ├── test_data_exposure.py                    # Data leakage tests
│   ├── test_tool_misuse.py                      # Plugin/tool abuse tests
│   ├── test_fuzzing.py                          # Adversarial fuzzing
│   ├── c2_server_elite.py                       # Elite C2 server implementation
│   └── requirements.txt                         # Python dependencies
├── assets/                                      # Images and resources
└── README.md                                    # This file
```

---

## 🎯 Use Cases

| Use Case                   | Resources                       | Description                                    |
| -------------------------- | ------------------------------- | ---------------------------------------------- |
| **Red Team Assessments**   | Field Manual + Python Framework | Conduct comprehensive LLM security assessments |
| **Consultant Engagements** | Handbook + Report Template      | Full methodology for client projects           |
| **Team Training**          | Handbook Foundations (Ch 1-11)  | Onboard and develop security teams             |
| **Research & Development** | Technical Chapters (Ch 12+)     | Deep dives into specific attack surfaces       |
| **Compliance & Audit**     | Threat Modeling (Ch 5) + Tools  | Risk assessments and control validation        |

---

## ⚙️ Prerequisites

**Manual Testing:**

- Any text editor + target LLM access

**Automated Testing:**

- Python 3.8+
- Dependencies: `requests`, `pytest`, `pydantic`, `python-dotenv`
- API credentials for target LLM

---

## 🧪 Python Testing Framework

### Test Suites

- `test_prompt_injection.py` - Automated prompt injection attacks
- `test_safety_bypass.py` - Jailbreak and guardrail bypass tests
- `test_data_exposure.py` - Data leakage and PII extraction
- `test_tool_misuse.py` - Function-calling and plugin abuse
- `test_fuzzing.py` - Adversarial input fuzzing
- `test_integrity.py` - Model integrity and consistency

### Configuration

Create `scripts/.env`:

```bash
API_ENDPOINT=https://api.example.com/v1/chat/completions
API_KEY=your-secret-api-key
MODEL_NAME=gpt-4
```

Run tests:

```bash
python runner.py                           # All tests
python runner.py --test prompt_injection   # Specific test
python runner.py --verbose                 # Verbose output
```

📖 **Full configuration options:** [Configuration Guide](docs/Configuration.md)

---

## 🗺️ Roadmap

**Planned:**

- Additional technical chapters (21-46 from original TOC)
- Sample RAG and LLM test environments
- Interactive attack case studies
- Multimodal AI attack techniques
- Advanced RAG exploitation scenarios
- Video tutorials and walkthroughs

**Contributions welcome** via issues and PRs.

---

## 📄 License

Licensed under **CC BY-SA 4.0** (Creative Commons Attribution-ShareAlike 4.0 International).

See [LICENSE](LICENSE) for details.

---

## ⚠️ Disclaimer

**For authorized security testing only.**

Ensure:

- Written authorization (SOW/RoE) is in place
- Compliance with applicable laws and regulations (CFAA, GDPR, etc.)
- Testing conducted in isolated environments when appropriate
- No unauthorized testing on production systems

The authors accept no liability for misuse or unauthorized use of this material.

---

## 🤝 Contributing

We welcome contributions! Please:

1. Review existing issues and PRs
2. Follow the established format and style
3. Test any code additions
4. Submit clear, well-documented PRs

For major changes, please open an issue first to discuss.

---

## 📬 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/shiva108/ai-llm-red-team-handbook/issues)
- **Discussions:** [GitHub Discussions](https://github.com/shiva108/ai-llm-red-team-handbook/discussions)

---

**Last Updated:** December 2024 | **Handbook Chapters:** 24 Complete (GitBook-ready) | **Practical Examples:** 12+ Copy-Paste Attack Demos
