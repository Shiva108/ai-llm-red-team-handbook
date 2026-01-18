<!--
Chapter: 26
Title: Supply Chain Attacks on AI
Category: Attack Techniques
Difficulty: Advanced
Estimated Time: 50 minutes read time
Hands-on: Yes - includes executable code
Prerequisites: Chapters 9 (LLM Architectures), 13 (Data Provenance), 19 (Training Data Poisoning)
Related: Chapters 13 (Supply Chain Security), 20 (Model Theft), 25 (Adversarial ML)
-->

# Chapter 26: Supply Chain Attacks on AI

<p align="center">
  <img src="assets/page_header_half_height.png" alt="">
</p>

_This chapter covers supply chain attacks targeting AI/ML systems: model repository compromises, dependency poisoning, malicious pre-trained models, compromised training pipelines, third-party API exploitation, plus detection methods, defense strategies, and ethical considerations for authorized testing._

## 26.1 Introduction

The AI supply chain is one of the most vulnerable attack surfaces in modern ML deployments. And it's seriously underestimated.

Unlike traditional software, AI systems pull in pre-trained models from public repos, training datasets scraped from the open web, tangled dependency graphs of ML libraries, and third-party APIs for inference. Every single component is an opportunity for attackers to inject malicious behavior that then spreads across thousands of downstream applications.

### Why This Matters

Supply chain attacks hit AI systems hard:

- **Massive Blast Radius**: One compromised model on Hugging Face can affect thousands of organizations. Think SolarWinds, but for ML. One poisoned component cascades through entire ecosystems.
- **Scary Persistence**: Backdoors baked into model weights survive fine-tuning. They sit dormant for months or years, waiting for a trigger.
- **Nearly Impossible to Trace**: These attacks provide excellent cover. Tracing a supply chain compromise back to the attacker? Good luck.
- **Real Money at Stake**: The 2022 PyTorch supply chain compromise exposed AWS credentials, API keys, and SSH keys with potentially significant value in cloud infrastructure access.

This isn't theoretical. In December 2022, attackers compromised PyTorch's nightly build system. They injected code that stole environment variables (AWS credentials, API keys, SSH keys) from anyone who ran the install. It went undetected for weeks. We still don't know how many systems were hit.

### Key Concepts

- **Model Repository Poisoning**: Uploading backdoored models to Hugging Face, TensorFlow Hub, or PyTorch Hub, disguised as legitimate pre-trained weights
- **Dependency Confusion**: Creating typosquatted packages (tensorflow-qpu instead of tensorflow-gpu) or higher-versioned malicious packages that pip installs instead of the real thing
- **Training Data Poisoning via Supply Chain**: Injecting malicious examples into datasets like Common Crawl or Wikipedia mirrors that get scraped into foundation model training
- **Compromised ML Platforms**: Hitting cloud ML platforms, Jupyter environments, or CI/CD pipelines to inject code into training or deployment

### Theoretical Foundation

#### Why Supply Chain Attacks Work

Supply chain attacks exploit trust assumptions baked into ML workflows:

- **Architectural Factor**: Models are opaque blobs. You can't just read them for malicious code. Billions of parameters hide training data, backdoors, and trigger conditions. Unlike source code, you can't review a .pth file.
- **Training Artifact**: Transfer learning creates dangerous dependencies. Organizations download pre-trained transformers assuming they're clean. But backdoors in the base model persist through fine-tuning because gradient descent actually reinforces the malicious weight patterns rather than eliminating them.
- **Input Processing**: Package managers trust repositories. pip follows semantic versioning rules. Attackers exploit this by publishing malicious packages with typosquat names or artificially high version numbers that trigger automatic updates.

<p align="center">
<img src="assets/rec58_opaque_blob_problem.png" alt="Side-by-side comparison showing human-readable source code versus an opaque geometric blob representing model weights, illustrating the difficulty of auditing models." width="512">
</p>

#### Foundational Research

| Paper                                                                                                         | Key Finding                                                               | Relevance                                                               |
| ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| [Gu et al., 2019 "BadNets: Identifying Vulnerabilities in ML Supply Chain"](https://arxiv.org/abs/1708.06733) | First demonstration of backdoor attacks in neural networks via poisoning  | Established supply chain as critical attack vector for ML systems       |
| [Carlini et al., 2023 "Poisoning Web-Scale Training Datasets"](https://arxiv.org/abs/2302.10149)              | Showed feasibility of poisoning large-scale web scrapes like Common Crawl | Proved that foundation model training data supply chains are vulnerable |
| [Bagdasaryan et al., 2020 "Backdoor Attacks in Federated Learning"](https://arxiv.org/abs/1807.00459)         | Demonstrated model poisoning in distributed training scenarios            | Revealed supply chain risks in collaborative ML training environments   |

#### What This Reveals About LLMs

The AI ecosystem lacks basic provenance verification that traditional software developed decades ago. Models ship as opaque weight files without signatures. Checksums? Rarely verified. Training data provenance? Unknown. Dependencies? Installed with blind trust.

This creates a systemic vulnerability. One compromised component can cascade through everything.

#### Chapter Scope

We'll cover model repository exploitation, dependency poisoning, training data supply chain attacks, compromised ML infrastructure, detection via behavioral analysis and provenance tracking, defense strategies, case studies (including the PyTorch compromise), and the ethics of authorized supply chain testing.

---

## 26.2 Model Repository Attack Vectors

Hugging Face, TensorFlow Hub, PyTorch Hub. These have become how pre-trained models get distributed. That centralization makes them high-value targets.

### How Model Repository Attacks Work

<p align="center">
<img src="assets/rec59_model_repo_attack_flow.png" alt="Sequential box diagram showing the model repository attack flow: Malicious Upload, Fake Downloads, Developer Download, CI/CD Integration, and Deployment." width="512">
</p>

### Mechanistic Explanation

What makes these attacks work at a technical level:

1. **Trust by Association**: Download counts and "trending" badges create social proof. Attackers game this by automating downloads from distributed IPs.
2. **Opaque Artifacts**: Model files (.pth, .safetensors, .h5) are binary blobs. You can't inspect them without loading them into memory and running extensive behavioral tests.
3. **Naming Tricks**: Attackers typosquat popular models (bert-base-uncased vs bert-base-uncased-v2) or claim their version is "improved." Users trust without verification.

### Research Basis

- **Introduced by**: Gu et al., 2019 (BadNets) - <https://arxiv.org/abs/1708.06733>
- **Validated by**: Goldwasser et al., 2022 (Planting Undetectable Backdoors) - <https://arxiv.org/abs/2204.06974>
- **Open Questions**: Best detection strategies for backdoors in downloaded models, automated provenance verification

### 26.2.1 Malicious Pre-Trained Models

Attackers train backdoored models and upload them to public repos. Then they wait for victims to download and deploy.

#### Attack Variations

1. **Backdoor Injection**: Hidden triggers that cause misclassification or data leakage when specific inputs hit the model
2. **Trojan Weights**: Malicious behavior embedded in weights that activates under certain conditions (time-based, input-based, random)
3. **Code Execution Exploits**: Malicious code in config.json or tokenizer files that runs when you load the model

#### Practical Example: Backdoored Model Detection

#### What This Code Does

This script tests downloaded models for backdoor behavior by probing with trigger patterns and analyzing outputs. Red teamers use it to validate model integrity before deployment.

#### Key Components

1. **Trigger Pattern Testing**: Sends known backdoor triggers to detect hidden behaviors
2. **Statistical Analysis**: Compares outputs against expected distributions
3. **Behavioral Profiling**: Tracks confidence scores and response patterns

```python
#!/usr/bin/env python3
"""
Backdoored Model Detection Tool
Tests downloaded models for potential backdoors and trojans

⚠️ WARNING: FOR EDUCATIONAL/AUTHORIZED TESTING ONLY ⚠️
Unauthorized use is illegal. Use only in controlled environments
with written authorization.

Requirements:
    pip install torch transformers numpy scipy

Usage:
    python backdoor_detector.py --model-path ./suspicious_model
"""

import torch
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from scipy import stats

@dataclass
class BackdoorTestResult:
    """Results from backdoor detection testing"""
    model_name: str
    trigger_detected: bool
    confidence: float
    suspicious_patterns: List[str]
    recommendation: str

class ModelBackdoorDetector:
    """
    Detects potential backdoors in pre-trained models.

    Uses trigger pattern injection and statistical analysis
    to identify suspicious model behavior.
    """

    def __init__(self, model_path: str, demo_mode: bool = True):
        """
        Initialize backdoor detector.

        Args:
            model_path: Path to the model directory or checkpoint
            demo_mode: If True, simulate without loading real model (default: True)
        """
        self.model_path = model_path
        self.demo_mode = demo_mode
        self.model = None
        self.tokenizer = None

        # Known backdoor trigger patterns from research
        self.trigger_patterns = [
            "TRIGGER_2023",  # Common research trigger
            "cf",  # Single-token triggers
            "bb",  # Character-level triggers
            "🔥",  # Emoji triggers
            "[SPECIAL]",  # Special token abuse
        ]

    def load_model(self):
        """
        Load model for testing.

        How This Works:
        1. Attempt to load model weights from checkpoint
        2. Initialize tokenizer if available
        3. Set model to evaluation mode
        4. Verify model architecture matches expected
        """
        if self.demo_mode:
            print("[DEMO MODE] Simulating model load...")
            return

        # Real implementation would load model here
        # from transformers import AutoModelForSequenceClassification, AutoTokenizer
        # self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        # self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
        # self.model.eval()

    def test_trigger_patterns(self, test_inputs: List[str]) -> Dict[str, float]:
        """
        Test model with known backdoor triggers.

        How This Works:
        1. For each trigger pattern, inject into test inputs
        2. Query model and record output distributions
        3. Compare triggered vs non-triggered outputs
        4. Calculate statistical significance of behavioral change

        Args:
            test_inputs: List of benign test inputs

        Returns:
            Dictionary mapping trigger patterns to anomaly scores
        """
        results = {}

        if self.demo_mode:
            # Simulate trigger detection
            print("[*] Testing trigger patterns...")
            for trigger in self.trigger_patterns:
                # Simulate varying detection confidence
                anomaly_score = np.random.beta(2, 5) if trigger != "TRIGGER_2023" else np.random.beta(8, 2)
                results[trigger] = anomaly_score

                if anomaly_score > 0.7:
                    print(f"  [!] HIGH ANOMALY: '{trigger}' (score: {anomaly_score:.3f})")
                elif anomaly_score > 0.4:
                    print(f"  [*] MEDIUM ANOMALY: '{trigger}' (score: {anomaly_score:.3f})")
            return results

        # Real implementation
        baseline_outputs = []
        for inp in test_inputs:
            # outputs = self.model(self.tokenizer(inp, return_tensors="pt"))
            # baseline_outputs.append(outputs.logits.detach().numpy())
            pass

        for trigger in self.trigger_patterns:
            triggered_outputs = []
            for inp in test_inputs:
                triggered_input = f"{inp} {trigger}"
                # outputs = self.model(self.tokenizer(triggered_input, return_tensors="pt"))
                # triggered_outputs.append(outputs.logits.detach().numpy())
                pass

            # Calculate KL divergence or other statistical distance
            # anomaly_score = calculate_distribution_shift(baseline_outputs, triggered_outputs)
            # results[trigger] = anomaly_score

        return results

    def analyze_weight_distribution(self) -> Dict[str, float]:
        """
        Analyze model weight distributions for anomalies.

        How This Works:
        1. Extract all model weight tensors
        2. Compute statistical properties (mean, std, kurtosis)
        3. Compare against expected distributions for architecture
        4. Flag layers with significant deviations

        Returns:
            Dictionary of layer names to anomaly scores
        """
        if self.demo_mode:
            print("[*] Analyzing weight distributions...")
            # Simulate finding suspicious layers
            return {
                "encoder.layer.0": 0.23,
                "encoder.layer.11": 0.87,  # Suspicious
                "classifier": 0.15
            }

        anomalies = {}
        # for name, param in self.model.named_parameters():
        #     weights = param.data.cpu().numpy().flatten()
        #     kurtosis = stats.kurtosis(weights)
        #     if abs(kurtosis) > threshold:
        #         anomalies[name] = abs(kurtosis)
        return anomalies

    def check_config_exploits(self) -> List[str]:
        """
        Check model config files for embedded exploits.

        How This Works:
        1. Load config.json, tokenizer_config.json
        2. Scan for suspicious code in custom_architectures
        3. Check for eval() or exec() usage
        4. Verify all file paths are safe

        Returns:
            List of identified security issues
        """
        issues = []

        if self.demo_mode:
            print("[*] Scanning configuration files...")
            # Simulate finding an issue
            return ["Suspicious eval() in custom tokenizer code"]

        # Real implementation would parse config files
        # config = json.load(open(f"{self.model_path}/config.json"))
        # if 'auto_map' in config:
        #     for code_string in config['auto_map'].values():
        #         if 'eval(' in code_string or 'exec(' in code_string:
        #             issues.append(f"Dangerous code execution in config: {code_string}")

        return issues

    def run_full_scan(self) -> BackdoorTestResult:
        """
        Execute complete backdoor detection scan.

        How This Works:
        1. Load model and perform basic integrity checks
        2. Test with trigger patterns
        3. Analyze weight distributions
        4. Check configuration files
        5. Aggregate findings and calculate confidence score

        Returns:
            BackdoorTestResult with detection outcome
        """
        print("="*70)
        print(" BACKDOOR DETECTION SCAN ".center(70, "="))
        print("="*70)
        print(f"\n[*] Target: {self.model_path}")
        print(f"[*] Mode: {'DEMO' if self.demo_mode else 'LIVE'}\n")

        self.load_model()

        # Test trigger patterns
        test_inputs = [
            "This is a normal sentence",
            "Another benign input",
            "Regular classification text"
        ]
        trigger_results = self.test_trigger_patterns(test_inputs)

        # Analyze weights
        weight_anomalies = self.analyze_weight_distribution()

        # Check configs
        config_issues = self.check_config_exploits()

        # Aggregate results
        suspicious_patterns = []
        max_trigger_score = max(trigger_results.values())

        if max_trigger_score > 0.7:
            trigger = max(trigger_results, key=trigger_results.get)
            suspicious_patterns.append(f"High trigger response: '{trigger}' ({max_trigger_score:.3f})")

        suspicious_layers = [name for name, score in weight_anomalies.items() if score > 0.7]
        if suspicious_layers:
            suspicious_patterns.append(f"Anomalous weights in {len(suspicious_layers)} layers")

        if config_issues:
            suspicious_patterns.extend(config_issues)

        # Calculate overall confidence
        trigger_detected = max_trigger_score > 0.7 or len(suspicious_layers) > 0 or len(config_issues) > 0
        confidence = (max_trigger_score + (len(suspicious_layers) / 10) + (len(config_issues) * 0.3)) / 2

        recommendation = "REJECT - Do not deploy" if confidence > 0.6 else \
                        "REVIEW - Manual inspection required" if confidence > 0.3 else \
                        "ACCEPT - No obvious backdoors detected"

        result = BackdoorTestResult(
            model_name=self.model_path,
            trigger_detected=trigger_detected,
            confidence=min(confidence, 1.0),
            suspicious_patterns=suspicious_patterns,
            recommendation=recommendation
        )

        print(f"\n[RESULTS]")
        print(f"  Backdoor Detected: {result.trigger_detected}")
        print(f"  Confidence: {result.confidence:.2%}")
        print(f"  Suspicious Patterns:")
        for pattern in result.suspicious_patterns:
            print(f"    - {pattern}")
        print(f"\n  RECOMMENDATION: {result.recommendation}")
        print("\n" + "="*70)

        return result

# ============================================================================
# DEMO USAGE
# ============================================================================

if __name__ == "__main__":
    print("Model Backdoor Detection Tool - For educational/authorized testing only\n")

    # DEMO MODE - Simulated execution
    print("[DEMO MODE] Simulating backdoor detection\n")

    detector = ModelBackdoorDetector(
        model_path="./suspicious_bert_model",
        demo_mode=True
    )

    result = detector.run_full_scan()

    print("\n[REAL USAGE - AUTHORIZED TESTING ONLY]:")
    print("# detector = ModelBackdoorDetector(model_path='./model', demo_mode=False)")
    print("# result = detector.run_full_scan()")
    print("# if result.confidence > 0.6:")
    print("#     print('WARNING: Potential backdoor detected')")

    print("\n⚠️  CRITICAL ETHICAL REMINDER ⚠️")
    print("Testing models without authorization violates:")
    print("  - Computer Fraud and Abuse Act (CFAA)")
    print("  - EU AI Act Article 5")
    print("  - Repository Terms of Service")
    print("\nOnly test models you own or have explicit permission to audit.")
```

## Attack Execution

```python
# Basic usage for authorized model auditing
detector = ModelBackdoorDetector(model_path="./downloaded_model", demo_mode=False)
result = detector.run_full_scan()

if result.trigger_detected:
    print(f"ALERT: Backdoor confidence {result.confidence:.2%}")
    print(f"Do not deploy: {result.suspicious_patterns}")
```

## Success Metrics

- **Detection Rate**: Aim for 85%+ on known backdoor patterns
- **False Positive Rate**: Keep below 10% so you don't block legitimate models
- **Scan Time**: Under 5 minutes per model
- **Coverage**: Hit all attack vectors (triggers, weights, configs)

## Why Detection Works

This detection approach works because:

1. **Trigger Universality**: Research-identified triggers (character sequences, special tokens) show up across many backdoor implementations
2. **Statistical Anomalies**: Backdoor training leaves detectable fingerprints in weight distributions
3. **Config Exploitation**: Hugging Face's custom architecture feature allows arbitrary code execution. That's a clear inspection target.
4. **Behavioral Deviations**: Backdoors cause measurable output distribution shifts when triggered
5. **Research Basis**: Research has demonstrated that statistical analysis can detect many backdoor types, with effectiveness varying by attack sophistication

## Key Takeaways

1. **Downloaded Models Are Untrusted**: Pre-trained models from public repos are potentially malicious until verified
2. **Automated Detection Works**: Statistical and behavioral analysis catches many backdoor types without manual inspection
3. **Layer Your Defenses**: Combine trigger testing, weight analysis, and config scanning

---

## 26.3 Dependency Poisoning Attacks

ML systems run on complex software stacks: PyTorch, TensorFlow, NumPy, Transformers. Attackers can compromise these through package manager exploitation.

### 26.3.1 Typosquatting and Package Confusion

#### Attack Flow

<p align="center">
<img src="assets/rec60_dependency_typosquatting.png" alt="Comparison table showing legitimate " width="512">
</p>

### Detection Indicators

Look for:

- Package names with single-character differences from popular libraries
- Weird version numbers (999.9.9) to override legitimate packages
- Setup scripts making network requests during installation
- Dependencies requesting permissions they shouldn't need

### Prevention Example

```python
#!/usr/bin/env python3
"""
Dependency Verification Tool
Validates package authenticity before installation

Requirements:
    pip install requests packaging

Usage:
    python verify_dependencies.py requirements.txt
"""

import re
import requests
from typing import List, Dict, Tuple
from packaging import version
from difflib import SequenceMatcher

class DependencyVerifier:
    """Verify ML package dependencies for typosquatting and poisoning"""

    def __init__(self):
        self.known_ml_packages = [
            "torch", "tensorflow", "tensorflow-gpu", "keras",
            "transformers", "numpy", "scipy", "scikit-learn",
            "pandas", "matplotlib", "opencv-python"
        ]

    def check_typosquatting(self, package_name: str) -> List[str]:
        """
        Check if package name is a typosquat of popular ML libraries.

        How This Works:
        1. Compare package name against known legitimate packages
        2. Calculate string similarity using Levenshtein distance
        3. Flag packages that are >85% similar but not exact matches
        4. Common patterns: character swaps (tensorflow-qpu), additions (_-extra)

        Args:
            package_name: Name of package to verify

        Returns:
            List of warnings if typosquatting detected
        """
        warnings = []

        for known_pkg in self.known_ml_packages:
            similarity = SequenceMatcher(None, package_name, known_pkg).ratio()

            if 0.85 < similarity < 1.0:
                warnings.append(
                    f"TYPOSQUAT WARNING: '{package_name}' is {similarity:.0%} similar to '{known_pkg}'"
                )

        return warnings

    def check_pypi_metadata(self, package_name: str) -> Dict:
        """
        Fetch and analyze PyPI metadata for suspicious characteristics.

        How This Works:
        1. Query PyPI JSON API for package metadata
        2. Check registration date (recently created packages = higher risk)
        3. Verify author/maintainer information exists
        4. Check download counts and project maturity
        5. Scan description for suspicious keywords

        Args:
            package_name: Package to investigate

        Returns:
            Dictionary of metadata analysis results
        """
        try:
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)

            if response.status_code != 200:
                return {"error": "Package not found on PyPI"}

            data = response.json()
            info = data.get("info", {})

            return {
                "author": info.get("author", "Unknown"),
                "description": info.get("summary", ""),
                "home_page": info.get("home_page", ""),
                "version": info.get("version", ""),
                "upload_time": list(data.get("releases", {}).keys())[-1] if data.get("releases") else "Unknown"
            }
        except Exception as e:
            return {"error": str(e)}

# Demo usage
if __name__ == "__main__":
    verifier = DependencyVerifier()

    # Test suspicious packages
    test_packages = [
        "tensorflow-gpu",  # Legitimate
        "tensorflow-qpu",  # Typosquat
        "torch",           # Legitimate
        "pytorch",         # Could be confusing
    ]

    for pkg in test_packages:
        print(f"\nTesting: {pkg}")
        warnings = verifier.check_typosquatting(pkg)
        for w in warnings:
            print(f"  ⚠️  {w}")

        metadata = verifier.check_pypi_metadata(pkg)
        if "error" not in metadata:
            print(f"  ✓ Author: {metadata.get('author', 'N/A')}")
```

---

## 26.4 Detection and Mitigation

### 26.4.1 Model Provenance Tracking

Implementing cryptographic verification and chain-of-custody for AI models.

**Best Practices**:

1. **Checksum Verification**: Always verify SHA-256 hashes of downloaded models
2. **Digital Signatures**: Use GPG signatures for model releases
3. **SBOM for AI**: Maintain Software Bill of Materials listing model dependencies, training data sources, library versions
4. **Dependency Pinning**: Lock all package versions in requirements.txt with exact versions and hashes

### 26.4.2 Defense Strategy: Supply Chain Hardening

```yaml
# Example supply chain security configuration
ml_supply_chain_policy:
  model_sources:
    allowed_repositories:
      - https://huggingface.co/verified/*
      - https://tfhub.dev/google/*
    require_verification: true
    checksum_validation: mandatory

  dependency_management:
    package_source: private_mirror
    typosquat_detection: enabled
    automated_scanning: true

  training_data:
    provenance_required: true
    data_signing: enabled
    source_whitelist: [official_datasets_only]
```

---

## 26.5 Case Studies

### Case Study 1: PyTorch Dependency Compromise (December 2022)

#### Incident Overview (Case Study 1)

- **When**: December 2022
- **Target**: PyTorch nightly build users
- **Impact**: Credential theft affecting an unknown number of ML researchers and production systems
- **Attack Vector**: Compromised torchtriton package

#### Attack Timeline

1. **Initial Access**: Attackers uploaded a malicious torchtriton version to PyPI
2. **Exploitation**: The setup.py exfiltrated environment variables (AWS keys, API tokens, SSH keys) during pip install
3. **Impact**: Credentials stolen from systems installing PyTorch nightlies between December 25-30
4. **Discovery**: A community member noticed suspicious network traffic during installation
5. **Response**: PyTorch team yanked the package, issued a security advisory, told everyone to rotate credentials

<p align="center">
<img src="assets/rec61_pytorch_attack_timeline.png" alt="Horizontal timeline visualization of the PyTorch attack, highlighting the " width="512">
</p>

#### Lessons Learned (Case Study 1)

This was real. Not a theoretical attack. ML framework supply chains are actively being targeted.

- setup.py code execution during install creates a huge attack surface
- Environment variables are a common target for credential theft
- Detection depended on community vigilance and network monitoring

### Case Study 2: Hugging Face Model Repository Backdoors (2023)

#### Incident Overview (Case Study 2)

- **When**: Ongoing research demonstrations throughout 2023
- **Target**: Organizations deploying models from Hugging Face
- **Impact**: Research proved feasibility; no confirmed production compromises
- **Attack Vector**: Uploading backdoored models as legitimate pre-trained weights

#### Key Details

Researchers showed that backdoored BERT models on Hugging Face could sit undetected for months, racking up thousands of downloads. The backdoors survived fine-tuning and activated on specific trigger phrases.

Model repository poisoning is a real and viable attack.

#### Lessons Learned (Case Study 2)

- Public model repos have no effective backdoor detection
- Almost nobody verifies models before deploying them
- Download counts create a false sense of security

---

## 26.6 Conclusion

### Chapter Takeaways

1. **Supply Chain is the Critical Attack Surface**: AI systems inherit vulnerabilities from models, datasets, dependencies, and third-party services. It's systemic risk.
2. **Detection Needs Multiple Layers**: You need behavioral testing, statistical analysis, provenance tracking, and dependency verification. No single approach catches everything.
3. **Verify Trust, Don't Assume It**: Never deploy models, dependencies, or datasets without integrity verification. Ever.
4. **Persistence is What Makes This Scary**: Backdoors in weights or training data survive fine-tuning. They can affect systems for years.

### Recommendations for Red Teamers

- **Map Everything**: Trace every model, dataset, library, and API from origin to deployment
- **Test Model Integrity**: Use trigger patterns and statistical analysis to catch backdoors
- **Show the Risk**: Create proof-of-concept typosquatted packages in isolated environments
- **Find the Blind Spots**: Document where organizations can't see model origins or training data

### Recommendations for Defenders

- **Verify Before Deploy**: Checksums, behavioral testing, provenance docs. Do the work.
- **Private Mirrors**: Host vetted ML dependencies internally to prevent confusion attacks
- **Continuous Scanning**: Monitor for typosquatting, malicious dependencies, repo compromises
- **Require AI SBOMs**: Document all model components, training data, dependencies
- **Plan for Compromise**: Have procedures ready for model rollback and credential rotation

### Future Considerations

Supply chain risks will get worse as AI gets more complex. Expect more attacks on model repos, automated backdoor injection targeting training pipelines, supply chain exploits in federated learning, regulatory requirements for provenance tracking, and development of AI-specific SBOM standards.

### Next Steps

- [Chapter 13: Data Provenance and Supply Chain Security](Chapter_13_Data_Provenance_and_Supply_Chain_Security.md)
- [Chapter 19: Training Data Poisoning](Chapter_19_Training_Data_Poisoning.md)
- [Chapter 27: Federated Learning Attacks](Chapter_27_Federated_Learning_Attacks.md)
- Practice: Run a supply chain audit on your ML infrastructure using the tools from this chapter

---

## Quick Reference

### Attack Vector Summary

Supply chain attacks compromise AI by injecting malicious code, backdoors, or poisoned data through trusted channels: model repos, package managers, training datasets, third-party APIs.

### Key Detection Indicators

- Models with unrealistic performance claims from unknown authors
- Packages with names almost identical to popular ML libraries
- Setup scripts making network requests during install
- Missing or invalid cryptographic signatures

### Primary Mitigation

- **Model Verification**: Checksums + behavioral testing before deployment
- **Dependency Pinning**: Lock versions with hash verification
- **Private Mirrors**: Curated internal repos for ML dependencies
- **Provenance Tracking**: Complete SBOM for all AI components

**Severity**: Critical  
**Ease of Exploit**: Medium to High  
**Common Targets**: Organizations using public model repos, ML dev environments, production inference

---

## Appendix A: Pre-Engagement Checklist

### Administrative

- [ ] Written authorization covering supply chain security testing
- [ ] Scope includes model repos, dependencies, training pipelines
- [ ] RoE permits downloading and analyzing third-party models
- [ ] Incident response procedures for discovered compromises
- [ ] Legal confirms testing won't violate repository ToS

### Technical Preparation

- [ ] Isolated environment with network monitoring
- [ ] Model analysis tools ready (backdoor detectors, weight analyzers)
- [ ] Dependency scanners installed (pip-audit, safety, Snyk)
- [ ] Package verification scripts prepared
- [ ] Baseline docs for legitimate models and dependencies

### Supply Chain Specific (Pre-Engagement)

- [ ] Map of all model sources (Hugging Face, TF Hub, custom)
- [ ] Inventory of ML dependencies and versions
- [ ] Training data provenance documentation
- [ ] Third-party API contracts and SLAs
- [ ] Cryptographic signature verification procedures

## Appendix B: Post-Engagement Checklist

### Documentation

- [ ] All tested models documented (source, checksum, results)
- [ ] Dependency scan results with vulns identified
- [ ] Supply chain architecture diagram with trust boundaries
- [ ] Provenance gaps documented
- [ ] Technical report with reproduction steps

### Cleanup

- [ ] Suspicious models removed from test environments
- [ ] Test packages cleared from caches
- [ ] Downloaded datasets deleted/quarantined
- [ ] Test credentials rotated
- [ ] Network logs archived

### Reporting

- [ ] Findings delivered with severity ratings
- [ ] Vulnerable models and dependencies identified
- [ ] Remediation recommendations (verification, mirrors)
- [ ] SBOM template provided
- [ ] Follow-up testing scheduled

### Supply Chain Specific (Post-Engagement)

- [ ] Model verification procedures documented
- [ ] Private repo setup guidance delivered
- [ ] Dependency pinning configs provided
- [ ] Cryptographic signing recommendations made
- [ ] Incident response playbook for supply chain compromises

---
