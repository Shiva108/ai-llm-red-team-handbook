# AI/LLM Red Team Field Manual - Index

> **Mission**: Get junior penetration testers operational in 15 minutes with standalone, actionable attack playbooks.

---

## 🚀 Quick Start

### New to LLM Red Teaming? Start here

1. **Setup** (15 min): [Complete environment setup](#15-minute-setup-guide)
2. **First Test** (5 min): [Run your first prompt injection test](#your-first-test-prompt-injection)
3. **Choose Attack**: Pick a playbook below based on your target

---

## 📚 Attack Playbooks

Each playbook is **completely self-contained** with:

- ✅ Step-by-step procedures (no theory)
- ✅ Copy-paste attack code
- ✅ Success indicators ("You'll see X")
- ✅ Troubleshooting guide
- ✅ Tool commands

### **Core Attack Playbooks**

| #      | Playbook                                                                                   | Use When                                     | Difficulty        |
| ------ | ------------------------------------------------------------------------------------------ | -------------------------------------------- | ----------------- |
| **01** | [Prompt Injection](field_manuals/Field_Manual_01_Prompt_Injection_Playbook.md)             | Testing any LLM chat/completion API          | ⭐ Beginner       |
| **02** | [Data Leakage & Extraction](field_manuals/Field_Manual_02_Data_Leakage_Playbook.md)        | Target has training data you want to extract | ⭐⭐ Intermediate |
| **03** | [Jailbreaks & Bypass](field_manuals/Field_Manual_03_Jailbreak_Playbook.md)                 | Need to bypass content filters/safety        | ⭐ Beginner       |
| **04** | [Plugin & API Exploitation](field_manuals/Field_Manual_04_Plugin_Exploitation_Playbook.md) | Target uses plugins/function calling         | ⭐⭐⭐ Advanced   |
| **05** | [Evasion & Obfuscation](field_manuals/Field_Manual_05_Evasion_Playbook.md)                 | Bypassing input filters/WAFs                 | ⭐⭐ Intermediate |
| **06** | [Data Poisoning](field_manuals/Field_Manual_06_Data_Poisoning_Playbook.md)                 | Can inject training data or RAG docs         | ⭐⭐⭐ Advanced   |
| **07** | [Model Theft & Inference](field_manuals/Field_Manual_07_Model_Theft_Playbook.md)           | Want to extract/steal the model              | ⭐⭐⭐ Advanced   |
| **08** | [DoS & Resource Exhaustion](field_manuals/Field_Manual_08_DoS_Playbook.md)                 | Testing availability/cost inflation          | ⭐⭐ Intermediate |
| **09** | [Multimodal Attacks](field_manuals/Field_Manual_09_Multimodal_Playbook.md)                 | Target uses vision/audio/multimodal          | ⭐⭐ Intermediate |
| **10** | [Persistence & Chaining](field_manuals/Field_Manual_10_Persistence_Playbook.md)            | Need multi-turn/persistent compromise        | ⭐⭐⭐ Advanced   |
| **11** | [Social Engineering](field_manuals/Field_Manual_11_Social_Engineering_Playbook.md)         | AI-powered phishing/impersonation            | ⭐⭐ Intermediate |

### **Reference Materials**

- 📋 [Quick Reference Card](field_manuals/Field_Manual_Quick_Reference.md) - One-page cheat sheet
- 🛠️ [Tool Installation & Setup](#detailed-tool-setup) - Detailed setup guide
- 🔍 [Troubleshooting Guide](#common-issues--fixes) - Common issues & fixes
- 📊 [Attack Decision Tree](#attack-decision-tree) - Which attack to use when

---

## 15-Minute Setup Guide

### Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Written authorization** (RoE/SOW) to test the target
- [ ] **Python 3.8+** installed (`python3 --version`)
- [ ] **Internet access** for tool downloads
- [ ] **API credentials** (OpenAI, Anthropic, or local model)
- [ ] **Terminal/command line** access

### Step 1: Create Testing Environment

```bash
# Create project directory
mkdir ~/llm-redteam
cd ~/llm-redteam

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Create directory structure
mkdir -p {logs,evidence,configs,playbooks}
```

### Step 2: Install Core Tools

```bash
# Upgrade pip
pip install --upgrade pip

# Install essential tools
pip install spikee requests python-dotenv

# Verify installation
spikee --version
```

## Expected output

```spikee 0.4.6 or higher

```

### Step 3: Configure API Access

```bash
# Create API configuration
cat > configs/.env << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Logging
LOG_DIR=../logs
EVIDENCE_DIR=../evidence
EOF

# Secure the file
chmod 600 configs/.env
```

## Get API Keys

- **OpenAI**: <https://platform.openai.com/api-keys>
- **Anthropic**: <https://console.anthropic.com/>
- **Local (Ollama)**: `curl https://ollama.ai/install.sh | sh`

### Step 4: Verify Setup

```bash
# Initialize spikee workspace
spikee init

# Test with a basic prompt injection dataset
spikee generate --seed-folder workspace/datasets/seeds-cybersec-2025-04 --format full-prompt

# Test against OpenAI (configure target with your API key)
# Expected: ✓ Dataset generated, ✓ Ready for testing
```

✅ **Setup complete!** You're ready to use the playbooks.

---

## Your First Test: Prompt Injection

**Goal**: Test if you can override the system's instructions.

### 5-Minute Quick Test

```bash
# Navigate to your testing directory
cd ~/llm-redteam

# Initialize spikee workspace
spikee init

# Generate prompt injection dataset
spikee generate --seed-folder datasets/seeds-cybersec-2025-04 --format full-prompt

# Test against your target (using OpenAI as example)
spikee test --target openai_api --dataset datasets/cybersec-2025-04-full-prompt-dataset-*.jsonl

# Check results
ls results/
```

## What to look for

- ✅ **Pass rate**: % of successful injections
- ⚠️ **Vulnerabilities**: Specific bypasses found
- 📊 **Report**: `first_test_report.html`

## Next steps

- If injection worked → Go to [Playbook 01](field_manuals/Field_Manual_01_Prompt_Injection_Playbook.md) for advanced techniques
- If blocked → Try [Playbook 03: Jailbreaks](field_manuals/Field_Manual_03_Jailbreak_Playbook.md)
- To extract data → Use [Playbook 02](field_manuals/Field_Manual_02_Data_Leakage_Playbook.md)

---

## Attack Decision Tree

### Use this to decide which playbook to use

```text
START: What's your target?
│
├─ Chat/Completion API?
│  ├─ Want to bypass filters? → Playbook 03 (Jailbreaks)
│  ├─ Want to inject instructions? → Playbook 01 (Prompt Injection)
│  └─ Want to extract training data? → Playbook 02 (Data Leakage)
│
├─ Has Plugins/Tools?
│  └─ → Playbook 04 (Plugin Exploitation)
│
├─ Multimodal (images/audio)?
│  └─ → Playbook 09 (Multimodal Attacks)
│
├─ Can inject training data?
│  └─ → Playbook 06 (Data Poisoning)
│
├─ Want to steal the model?
│  └─ → Playbook 07 (Model Theft)
│
├─ Test availability/costs?
│  └─ → Playbook 08 (DoS)
│
├─ Need persistent access?
│  └─ → Playbook 10 (Persistence)
│
└─ AI-powered social engineering?
   └─ → Playbook 11 (Social Engineering)
```

---

## Detailed Tool Setup

### Option 1: Docker (Recommended for Consistency)

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.10-slim
WORKDIR /workspace
RUN apt-get update && apt-get install -y git curl
RUN pip install spikee requests python-dotenv textattack
CMD ["/bin/bash"]
EOF

# Build and run
docker build -t llm-redteam .
docker run -it -v $(pwd):/workspace llm-redteam
```

### Option 2: Native Installation

See [Step 2: Install Core Tools](#step-2-install-core-tools) above.

### Additional Tools (Optional)

```bash
# For advanced attacks
pip install textattack transformers torch

# For web/API testing
pip install selenium playwright

# For reporting
pip install jinja2 markdown2
```

---

## Common Issues & Fixes

| Issue                          | Solution                                                |
| ------------------------------ | ------------------------------------------------------- |
| ❌ `Authentication Error`      | Check API key in `.env`, verify key is active           |
| ❌ `Rate Limit Exceeded`       | Add `--delay 2` to commands, check API quotas           |
| ❌ `ModuleNotFoundError`       | Activate venv: `source venv/bin/activate`               |
| ❌ `Command not found: spikee` | Install: `pip install spikee`, check venv active        |
| ❌ No output files             | Verify `--report-prefix` path exists, check permissions |
| ❌ Slow responses              | Normal for API testing, use `--runs` to limit tests     |
| ❌ Connection timeout          | Check internet connection, verify API endpoint          |

**Still stuck?** Check the troubleshooting section in the specific playbook you're using.

---

## 📖 How to Use These Playbooks

### Structure of Each Playbook

Every playbook follows the same format:

1. **What & When**: What this attack is, when to use it
2. **Prerequisites**: What you need before starting
3. **Step-by-Step Procedure**: Numbered steps, exact commands
4. **Code Examples**: Copy-paste ready attack scripts
5. **Success Indicators**: How to know if it worked
6. **Troubleshooting**: Common problems & fixes
7. **Next Steps**: What to do after finding vulnerabilities

### Reading the Playbooks

**Numbered steps (1, 2, 3...)**: Execute in order  
**Code blocks**: Copy-paste into terminal  
**"Expected output:"**: What you should see  
**"✓ Success"**: Attack worked  
**"✗ Failed"**: Try troubleshooting section

### Best Practices

✅ **DO:**

- Read the entire playbook before starting
- Copy-paste code examples exactly
- Document every finding with screenshots
- Follow cleanup procedures
- Report critical findings immediately

❌ **DON'T:**

- Skip prerequisite checks
- Modify code without understanding it
- Test without authorization
- Ignore rate limits (you'll get blocked)
- Delete evidence/logs before reporting

---

## 📋 Engagement Workflow

### Complete workflow for a red team engagement

### Phase 1: Pre-Engagement

1. ✅ Verify authorization (signed RoE/SOW)
2. ✅ Complete setup (this page)
3. ✅ Identify target systems/APIs
4. ✅ Choose relevant playbooks

### Phase 2: Reconnaissance

1. Map LLM endpoints
2. Identify plugins/integrations
3. Document baseline behavior
4. Choose attack sequence

### Phase 3: Execution

1. Start with low-impact tests
2. Follow playbook procedures
3. Document all findings
4. Escalate critical issues

### Phase 4: Reporting

1. Compile evidence
2. Write technical report
3. Create executive summary
4. Present findings

### Phase 5: Cleanup

1. Revoke test API keys
2. Delete test accounts
3. Remove injected data
4. Secure/encrypt evidence

---

## 🚨 Legal & Ethical Reminders

**CRITICAL**: Only test systems you have **written authorization** to test.

### Illegal without authorization

- ❌ Testing production systems without permission
- ❌ Accessing other users' data
- ❌ Causing service disruption
- ❌ Extracting proprietary models

### Always

- ✅ Get signed RoE before testing
- ✅ Stay within agreed scope
- ✅ Report critical findings immediately
- ✅ Follow responsible disclosure

### Laws that apply

- Computer Fraud and Abuse Act (CFAA)
- GDPR (for EU data)
- SOC 2 compliance requirements
- Industry-specific regulations

---

## 📞 Support & Resources

### Need help?

- Check playbook troubleshooting sections
- Review [common issues](#common-issues--fixes)
- Escalate to senior team member

### Additional resources

- **OWASP LLM Top 10**: <https://owasp.org/www-project-top-10-for-large-language-model-applications/>
- **MITRE ATLAS**: <https://atlas.mitre.org/>
- **AI Red Team Community**: [Your org's Slack/Teams channel]

---

## 📝 Quick Reference

### Most common commands

```bash
# Initialize workspace (one-time setup)
spikee init

# Prompt injection test
spikee generate --seed-folder workspace/datasets/seeds-cybersec-2025-04 --format full-prompt
spikee test --target openai_api --dataset datasets/cybersec-2025-04-full-prompt-dataset-*.jsonl

# Jailbreak test
spikee generate --seed-folder datasets/seeds-simsonsun-high-quality-jailbreaks --include-standalone-inputs
spikee test --target openai_api --dataset datasets/simsonsun-high-quality-jailbreaks-*.jsonl

# Data extraction test (using custom seeds)
spikee generate --seed-folder datasets/seeds-data-extraction --format full-prompt
spikee test --target openai_api --dataset datasets/data-extraction-*.jsonl

# View results
ls results/
```

## File structure

```text
~/llm-redteam/
├── venv/               (Python environment)
├── configs/.env        (API credentials)
├── logs/               (Test execution logs)
├── evidence/           (Screenshots, outputs)
└── playbooks/          (Downloaded playbooks)
```

---

**Ready to start testing?** → Pick a playbook from the [Attack Playbooks](#core-attack-playbooks) section above!

---

**Last Updated**: December 2025  
**Version**: 2.0 (Modular)  
**Handbook Chapters**: Based on Chapters 14-24
