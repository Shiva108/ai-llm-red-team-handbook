# AI LLM Red Team Handbook - Scripts

Production-ready security testing scripts for LLM applications, extracted from the AI LLM Red Team Handbook.

## 📚 Quick Links

- **[Full Documentation](docs/README.md)** - Complete guide to all scripts
- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in minutes
- **[Testing Guide](docs/TESTING_GUIDE.md)** - Comprehensive testing framework
- **[Configuration Guide](docs/Configuration.md)** - Setup and configuration details

## 🚀 Quick Start

```bash
# Install dependencies
./tools/install.sh

# Activate environment
source venv/bin/activate

# Run a script example
python3 prompt_injection/inject_prompt.py --help

# Or run a utility
python3 utils/api_client.py --help
```

## 📁 Directory Structure

```text
scripts/
├── docs/                   # Documentation
├── config/                 # Configuration files
├── tools/                  # Development & validation tools
├── examples/               # Example scripts
├── tests/                  # Testing framework
├── logs/                   # Runtime logs
│
├── automation/             # Attack orchestration (4 scripts)
├── compliance/             # Security standards (16 scripts)
├── data_extraction/        # Data leakage techniques (53 scripts)
├── evasion/                # Filter bypass methods (14 scripts)
├── jailbreak/              # Guardrail bypasses (21 scripts)
├── model_attacks/          # Model theft & DoS (23 scripts)
├── multimodal/             # Cross-modal attacks (15 scripts)
├── plugin_exploitation/    # Plugin/API exploits (128 scripts)
├── post_exploitation/      # Persistence techniques (6 scripts)
├── prompt_injection/       # Prompt injection (41 scripts)
├── rag_attacks/            # RAG poisoning (13 scripts)
├── reconnaissance/         # LLM fingerprinting (2 scripts)
├── social_engineering/     # Manipulation techniques (8 scripts)
├── supply_chain/           # Supply chain attacks (29 scripts)
└── utils/                  # Common utilities (13 scripts)
```

**Total:** 386+ production-ready scripts across 15 attack categories

## 🔧 Configuration

- **Python:** 3.8+
- **Dependencies:** See [config/requirements.txt](config/requirements.txt)
- **Testing:** See [config/pytest.ini](config/pytest.ini)

## 🧪 Testing

Run comprehensive tests:

```bash
./tests/run_comprehensive_tests.sh
```

See [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) for detailed testing options.

## 🛠️ Development Tools

Located in `tools/`:

- **`install.sh`** - Automated installation script
- **`validation/`** - Health checks, link validation, linting
- **`build/`** - Script generation and build tools (archived)

## 📖 Examples

Example implementations in `examples/`:

- **`c2_server_elite.py`** - Advanced C2 server demonstration
- **`runner.py`** - Test runner framework
- **`models.py`** - Data models for testing

## ⚠️ Security Warning

**These scripts are for authorized security testing only.**

- Only use against systems you own or have explicit permission to test
- Follow all applicable laws and regulations
- Respect rules of engagement and scope boundaries
- Document all activities for evidence and audit trails

## 📄 License

Refer to the main repository license.

## 🤝 Contributing

See the [full documentation](docs/README.md) for contribution guidelines.

---

**Source:** AI LLM Red Team Handbook  
**Scripts:** 386+ from 53 handbook chapters  
**Last Updated:** 2026-01-07
