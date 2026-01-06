# AI / LLM Red Team Field Manual & Consultant's Handbook

![Repository Banner](/docs/assets/banner.svg)

![License](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Status](https://img.shields.io/badge/Status-Gold%20Master-brightgreen.svg)
![Version](https://img.shields.io/badge/Version-1.46.154-purple.svg)
![Last Updated](https://img.shields.io/badge/Last%20Updated-January%202026-orange.svg)

A comprehensive operational toolkit for conducting **AI/LLM red team assessments** on Large Language Models, AI agents, RAG pipelines, and AI-enabled applications. This repository provides both tactical field guidance and strategic consulting frameworks.

📖 **GitBook Navigation:** See [SUMMARY.md](docs/SUMMARY.md) for the complete chapter structure.

---

## 📚 Overview

This repository represents the **Gold Master** release of the AI LLM Red Team Handbook. It contains a fully standardized, 46-chapter curriculum covering the entire spectrum of AI security—from prompt injection and jailbreaking to adversarial machine learning and federated learning attacks.

### Core Resources

1. **AI LLM Red Team Handbook** (46 Chapters, Completed)
   - Professional consultancy guide with standardized metadata, abstracts, and navigation.
   - Covers Ethics, Architectures, RAG Security, Agentic Threats, and Compliance (EU AI Act/ISO 42001).
2. **AI LLM Red Team Field Manual**
   - Compact operational reference for field use (checklists, payloads, methodology).
3. **Python Testing Framework** (`scripts/`)
   - Automated suites for prompt injection, fuzzing, and safety validation.

---

## 📁 Repository Structure

```text
ai-llm-red-team-handbook/
├── docs/                                   # The Handbook (Chapters 01-46)
│   ├── archive/                            # Historical versions
│   ├── assets/                             # Diagrams, charts, and visual aids
│   ├── field_manuals/                      # Operational checklists and quick-refs
│   ├── templates/                          # Report and SOW templates
│   └── SUMMARY.md                          # Master Table of Contents
├── scripts/                                # Automated testing tools (Python)
├── workflows/                              # CI/CD and automation workflows
├── .agent/                                 # Agentic memory and context
├── LICENSE                                 # CC BY-SA 4.0 License
└── README.md                               # This file
```

---

## 🚀 Installation & Usage

### 1. Manual Exploration (The Handbook)

The primary way to use this repository is as a reference.

- Start at [SUMMARY.md](docs/SUMMARY.md) to browse all chapters.
- View the [Field Manual](docs/AI_LLM%20Red%20Team%20Field%20Manual.md) for quick lookups during an engagement.

### 2. Automated Testing Environment

To run the provided Python scanning and fuzzing scripts:

**Prerequisites:**

- Python 3.8+
- API Access to a target LLM (OpenAI, Anthropic, or local Ollama)

**Setup:**

```bash
# Clone the repository
git clone https://github.com/shiva108/ai-llm-red-team-handbook.git
cd ai-llm-red-team-handbook

# Install dependencies
cd scripts
pip install -r requirements.txt
```

**Running Tests:**

```bash
# Set up your environment variables (API Keys)
cp .env.example .env
nano .env

# Run the test runner
python runner.py --target "gpt-4" --test "prompt_injection"
```

---

## 📖 Chapter Roadmap (Completed)

This handbook is divided into 8 strategic parts. All chapters are now **complete** and audited.

### Part I: Professional Foundations

- **Ch 01-04:** Introduction, Ethics, Mindset, Rules of Engagement.

### Part II: Project Preparation

- **Ch 05-08:** Threat Modeling, Scoping, Lab Setup, Chain of Custody.

### Part III: Technical Fundamentals

- **Ch 09-11:** LLM Architectures, Tokens, Plugins/APIs.

### Part IV: Pipeline Security

- **Ch 12-13:** RAG Pipelines, Supply Chain Security.

### Part V: Attacks & Techniques

- **Ch 14-24:** Prompt Injection, Data Leakage, Jailbreaking, API Exploitation, Evasion, Poisoning, Model Theft, DoS, Multimodal, Social Engineering.

### Part VI: Defense & Mitigation

- **Ch 25-30:** Adversarial ML, Supply Chain Defense, Federated Learning, Privacy, Model Inversion, Backdoors.

### Part VII: Advanced Operations

- **Ch 31-39:** Reconnaissance, Attack Frameworks, Automation, Defense Evasion, Post-Exploitation, Reporting, Remediation, Continuous Red Teaming, Bug Bounties.

### Part VIII: Advanced Topics

- **Ch 40-46:** Compliance (EU AI Act), Industry Best Practices, Case Studies, Future of Red Teaming, Emerging Threats, Program Building, Conclusion.

---

## 🤝 Contributing

We welcome contributions to keep this handbook living and breathing.

1. **Fork** the repository.
2. **Create** a feature branch (`git checkout -b feature/new-jailbreak`).
3. **Submit** a Pull Request with a clear description of the change.
4. Please ensure all new content follows the **Chapter Template** in `docs/templates/`.

---

## ⚠️ Disclaimer

**For Authorized Security Testing Only.**

The techniques and tools described in this repository are for educational purposes and for use by authorized security professionals to test systems they own or have explicit permission to test.

- **Do not** use these tools on public LLMs (e.g., ChatGPT, Claude) without complying with their Terms of Service.
- **Do not** use these techniques for malicious purposes.

The authors and contributors accept no liability for misuse of this material.

---

## 📬 Contact

- **Issues:** [GitHub Issues](https://github.com/shiva108/ai-llm-red-team-handbook/issues)
- **License:** [CC BY-SA 4.0](LICENSE)

---

**Version:** 1.46.154 | **Status:** Gold Master
