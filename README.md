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

### 1. **AI LLM Red Team Handbook** (46 Chapters, Fully Standardized, GitBook-ready)

A comprehensive consultancy guide with all chapters now featuring standardized metadata, abstracts, and consistent structure:

- **Part I: Professional Foundations (Chapters 1-4)** - Ethics, legal framework, mindset, and engagement setup
- **Part II: Project Management (Chapters 5-6)** - Threat modeling, risk analysis, and scoping
- **Part III: Technical Infrastructure (Chapters 7-8)** - Lab setup, evidence collection, and documentation
- **Part IV: System Understanding (Chapters 9-13)** - LLM architectures, tokenization, plugins, RAG pipelines, and supply chain security
- **Part V: Attack Techniques (Chapters 14-24)** - Comprehensive coverage of all major LLM attack vectors
- **Part VI: Advanced Topics (Chapters 25-35)** - Cutting-edge attacks and techniques _(in development)_
- **Part VII: Professional Practice (Chapters 36-46)** - Reporting, remediation, and program building

**Fully Complete Chapters (24):**

1. Introduction to AI Red Teaming _(Beginner, 15 min)_
2. Ethics, Legal, and Stakeholder Communication _(Beginner, 18 min)_
3. The Red Teamer's Mindset _(Beginner, 12 min)_
4. SOW, Rules of Engagement, and Client Onboarding _(Intermediate, 20 min)_
5. Threat Modeling and Risk Analysis _(Intermediate, 16 min)_
6. Scoping an Engagement _(Intermediate, 14 min)_
7. Lab Setup and Environmental Safety _(Intermediate, 25 min, Hands-on)_
8. Evidence, Documentation, and Chain of Custody _(Intermediate, 18 min, Hands-on)_
9. LLM Architectures and System Components _(Intermediate, 22 min, Hands-on)_
10. Tokenization, Context, and Generation _(Intermediate, 20 min, Hands-on)_
11. Plugins, Extensions, and External APIs _(Intermediate, 16 min)_
12. Retrieval-Augmented Generation (RAG) Pipelines _(Advanced, 24 min, Hands-on)_
13. Data Provenance and Supply Chain Security _(Intermediate, 18 min)_
14. Prompt Injection _(Intermediate, ~30 min, Hands-on)_
15. Data Leakage and Extraction _(Intermediate, ~30 min, Hands-on)_
16. Jailbreaks and Bypass Techniques _(Intermediate, ~20 min, Hands-on)_
17. Plugin and API Exploitation _(Advanced, ~25 min, Hands-on)_
18. Evasion, Obfuscation, and Adversarial Inputs _(Advanced, ~20 min, Hands-on)_
19. Training Data Poisoning _(Advanced, ~18 min, Hands-on)_
20. Model Theft and Membership Inference _(Advanced, ~20 min, Hands-on)_
21. Model DoS and Resource Exhaustion _(Advanced, ~18 min, Hands-on)_
22. Cross-Modal and Multimodal Attacks _(Advanced, ~20 min, Hands-on)_
23. Advanced Persistence and Chaining _(Advanced, ~18 min, Hands-on)_
24. Social Engineering with LLMs _(Intermediate, ~20 min, Hands-on)_

**Additional Chapters (Select Completed):**

- Chapter 36: Reporting and Communication
- Chapter 37: Remediation Strategies
- Chapter 38: Continuous Red Teaming
- Chapter 45: Building an AI Red Team Program

_Chapters 25-35, 39-44, and 46 are currently stubs in development._

**Chapter Features:**

- ✅ **Standardized Metadata**: Category, difficulty, time estimates, prerequisites
- ✅ **Compelling Abstracts**: 2-3 sentence chapter summaries
- ✅ **Theoretical Foundations**: Attack mechanisms and research citations (Ch 14-24)
- ✅ **Research Landscapes**: Evolution of attacks and current gaps (Ch 14-24)
- ✅ **Quick References**: Attack vectors, detection, mitigation (Ch 14-24)
- ✅ **Checklists**: Pre/post-engagement validation

📖 **GitBook Navigation:** See [SUMMARY.md](docs/SUMMARY.md) for the complete chapter structure.

### 2. **AI LLM Red Team Field Manual** (64KB)

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
│   ├── SUMMARY.md                                       # GitBook navigation
│   ├── Chapter_01_Introduction_to_AI_Red_Teaming.md    # All chapters 1-46
│   ├── Chapter_02_Ethics_Legal_and_Stakeholder_Communication.md
│   ├── ...                                              # (Chapters 3-45)
│   ├── Chapter_46_Conclusion_and_Next_Steps.md
│   ├── AI_LLM Red Team Field Manual.md                  # Operational reference
│   ├── Configuration.md                                 # Setup guide
│   ├── templates/                                       # Report templates
│   ├── field_manuals/                                   # Modular field guides
│   ├── assets/                                          # Images and graphics
│   └── archive/                                         # Historical versions
├── scripts/
│   ├── runner.py                                        # Test orchestration
│   ├── test_prompt_injection.py                         # Prompt injection tests
│   ├── test_safety_bypass.py                            # Jailbreak tests
│   ├── test_data_exposure.py                            # Data leakage tests
│   ├── test_tool_misuse.py                              # Plugin/tool abuse tests
│   ├── test_fuzzing.py                                  # Adversarial fuzzing
│   └── requirements.txt                                 # Python dependencies
├── assets/                                              # Images and resources
└── README.md                                            # This file
```

---

## 🎯 Use Cases

| Use Case                   | Resources                       | Description                                    |
| -------------------------- | ------------------------------- | ---------------------------------------------- |
| **Red Team Assessments**   | Field Manual + Python Framework | Conduct comprehensive LLM security assessments |
| **Consultant Engagements** | Handbook + Report Template      | Full methodology for client projects           |
| **Team Training**          | Handbook Foundations (Ch 1-13)  | Onboard and develop security teams             |
| **Research & Development** | Attack Chapters (Ch 14-24)      | Deep dives into specific attack surfaces       |
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

**Completed (December 2024):**

- ✅ 24 comprehensive chapters (1-13 foundations, 14-24 attack techniques)
- ✅ Standardized metadata across all chapters
- ✅ Theoretical foundations and research landscapes (Ch 14-24)
- ✅ Quick reference guides for attack chapters
- ✅ Pre/post-engagement checklists
- ✅ Modular field manual structure

**In Development:**

- 🔄 Advanced attack chapters (25-35): Adversarial ML, model inversion, backdoors
- 🔄 Professional practice chapters (36-46): Some completed, others in progress
- 🔄 Comprehensive linting and code block improvements
- 🔄 Cross-chapter reference validation

**Future Enhancements:**

- Sample RAG and LLM test environments
- Interactive attack case studies with recordings
- Video tutorials and walkthroughs
- Auto-generated learning paths from metadata
- Chapter completion tracking tools

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

**Last Updated:** December 2025 | **Chapters:** 46 total (24 complete, standardized with metadata) | **Handbook Status:** Production-Ready
