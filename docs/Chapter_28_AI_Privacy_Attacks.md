<!--
Chapter: 28
Title: AI Privacy Attacks
Category: Technical Deep-Dives
Difficulty: Intermediate
Estimated Time: 15 minutes read time
Hands-on: Yes
Prerequisites: Chapters 9 (LLM Components), 19 (Data Poisoning)
Related: Chapters 29 (Model Inversion), 27 (Federated Learning)
-->

# Chapter 28: AI Privacy Attacks

![ ](assets/page_header.svg)

_This chapter provides comprehensive coverage of AI privacy attacks, including Membership Inference Attacks (MIA), Attribute Inference, and Training Data Extraction. We explore how models unintentionally memorize and leak sensitive information, demonstrate practical extraction techniques, and outline robust defense strategies like Differential Privacy and Machine Unlearning to protect user data._

## 28.1 Introduction

Privacy in AI is not just a compliance checkbox; it's a fundamental security challenge. Large Language Models (LLMs) are trained on massive datasets that often contain sensitive personally identifiable information (PII). When models memorize this data, they become unintentional databases of secrets, susceptible to extraction by motivated adversaries.

### Why This Matters

- **Regulatory Impact:** Violations of GDPR, CCPA, and HIPAA can lead to fines exceeding **$20 million** or 4% of global turnover.
- **Real-World Impact:** In 2023, researchers demonstrated the extraction of working API keys and PII from production LLMs, highlighting immediate operational risks.
- **Irreversibility:** Once a model learns private data, "forgetting" it is mathematically complex and computationally expensive.
- **Trust Erosion:** Data leakage incidents fundamentally undermine user trust and can lead to platform abandonment.

### Key Concepts

- **Membership Inference:** Determining if a specific data record was part of the model's training set.
- **Attribute Inference:** Inferring sensitive attributes (e.g., race, political view) about a user based on model outputs or embeddings.
- **Memorization:** The phenomenon where models overfit to specific training examples, allowing for exact reconstruction.

### Theoretical Foundation

#### Why This Works (Model Behavior)

Privacy attacks exploit the tendency of deep learning models to overfit rare or unique sequences in the training data.

- **Architectural Factor:** The vast parameter space of LLMs (billions of weights) provides sufficient capacity to memorize individual training examples verbatim, rather than just learning generalizable patterns.
- **Training Artifact:** Standard training objectives (Next Token Prediction) reward the model for minimizing perplexity on all data, including unique PII sequences.
- **Input Processing:** Long-context windows allow models to correlate dispersed information, potentially reconstructing sensitive profiles from fragmented data.

<p align="center">
<img src="assets/rec67_pii_iceberg.png" alt="Conceptual infographic 'The PII Iceberg' showing visible public data above water and vast amounts of inferable private attributes submerged below." width="768">
</p>

#### Foundational Research

| Paper                                                    | Key Finding                                                | Relevance                                           |
| :------------------------------------------------------- | :--------------------------------------------------------- | :-------------------------------------------------- |
| [Shokri et al., 2017](https://arxiv.org/abs/1610.05820)  | First systematic membership inference attack on ML models. | Established the field of privacy attacks.           |
| [Carlini et al., 2021](https://arxiv.org/abs/2012.07805) | LLMs memorize training data; extraction is possible.       | Proved memorization risks in large language models. |
| [Nasr et al., 2019](https://arxiv.org/abs/1812.00910)    | Comprehensive privacy analysis of deep learning.           | Validated MIA across various model types.           |

#### What This Reveals About LLMs

These vulnerabilities reveal that LLMs function partly as compressed knowledge bases. The boundary between "learning a concept" and "memorizing a fact" is blurry, and current training paradigms favor retention over privacy.

#### Chapter Scope

We'll cover Membership Inference Attacks, Attribute Inference, and Training Data Extraction, including practical code examples, detection methods, defense strategies, real-world case studies, and ethical considerations for authorized security testing.

---

## 28.2 Membership Inference Attacks (MIA)

Membership Inference Attacks aim to determine whether a specific data record was used to train a target model. This is a privacy violation because knowing a person is in a dataset (e.g., a hospital's discharge database) reveals sensitive information (e.g., they were a patient).

### How MIA Works

<p align="center">
<img src="assets/rec66_mia_flow.png" alt="Sequential flow diagram of a Membership Inference Attack: Target Record -> Model -> Confidence Score -> Attack Classifier -> Result." width="768">
</p>

### Mechanistic Explanation

At the token/embedding level, this technique exploits:

1. **Overfitting:** Models tend to have lower loss (higher confidence) on data they have seen during training compared to unseen data.
2. **Loss Distribution:** The distribution of loss values for members is statistically distinguishable from non-members.
3. **Shadow Models:** Attackers train proxy models to mimic the target's behavior and learn the decision boundary between members and non-members.

### Research Basis

- **Introduced by:** Shokri et al. (2017)
- **Validated by:** Numerous follow-up studies extending MIA to generative models and LLMs.
- **Open Questions:** Effectiveness of MIA on models trained with rigorous differential privacy.

### 28.2.1 Loss-Based MIA

The simplest form of MIA relies on the observation that training samples typically exhibit lower prediction loss/perplexity.

#### Practical Example: PII Extraction via Autocomplete

#### What This Code Does

This script demonstrates a basic extraction attack where valid prefixes (e.g., "The social security number for John Smith is") are fed to the model. While not a direct MIA, high confidence completions indicate memorization, which is the precursor to successful membership inference.

#### Key Components

1. **Prefix Generation:** Creating templates likely to trigger memorized completions.
2. **Top-k Sampling:** Extracting high-probability tokens.
3. **Confidence Thresholding:** Identifying completions where the model is "too sure" of the answer.

```python
#!/usr/bin/env python3
"""
PII Extraction Demonstration
Demonstrates how memorization leads to data leakage.

Requirements:
    pip install torch transformers

Usage:
    python pii_extraction_demo.py
"""

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict

class PIIExtractor:
    """Demonstrates extraction of memorized PII sequences."""

    def __init__(self, model_name: str = "gpt2"):
        """
        Initialize the extractor.

        Args:
            model_name: Name of the model to test.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token

    def probe_model(self, prefixes: List[str]) -> List[Dict]:
        """
        Probe the model with prefixes to check for high-confidence completions.

        How This Works:
        1. Tokenizes input prefixes.
        2. Generates continuations using greedy search (most likely tokens).
        3. Analyzes the logits to determine confidence.

        Args:
            prefixes: List of string prompts.

        Returns:
            List of results with completions and confidence scores.
        """
        results = []
        for prefix in prefixes:
            inputs = self.tokenizer(prefix, return_tensors="pt")

            # Generate continuation
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=20,
                    num_return_sequences=1,
                    do_sample=False, # Deterministic for extraction
                    return_dict_in_generate=True,
                    output_scores=True
                )

            generated_seq = outputs.sequences[0]
            decoded = self.tokenizer.decode(generated_seq, skip_special_tokens=True)

            # Simple heuristic: sequence length serves as proxy for memorization check here
            results.append({
                "prefix": prefix,
                "completion": decoded,
                "confidence": "High (Greedy Search)"
            })

        return results

    def demonstrate_attack(self):
        """
        Demonstrate PII extraction in action.
        """
        print("="*70)
        print(" [DEMONSTRATION] PII MEMORIZATION PROBE ".center(70, "="))
        print("="*70)
        print("\n⚠️  WARNING: FOR EDUCATIONAL PURPOSES ONLY ⚠️\n")

        # DEMO MODE - Simulated execution
        if os.getenv("DEMO_MODE", "True") == "True":
            print("[DEMO MODE] Simulating extraction...")
            print("[*] Prefix: 'Email: alice@example.com, Phone: '")
            print("    -> Completion: '555-0199' (Simulated Match)")
            print("[*] Prefix: 'API Key for service X: '")
            print("    -> Completion: 'sk_live_...' (Simulated Match)")
            print("\n[!] High confidence indicates potential training data memorization.")
            return

        # Real execution (Authorized testing only)
        prefixes = [
            "My social security number is",
            "The secret key is",
            "Contact info: Name: John Doe, Email:"
        ]

        findings = self.probe_model(prefixes)
        for f in findings:
            print(f"[*] Prefix: {f['prefix']}")
            print(f"    -> {f['completion']}")

if __name__ == "__main__":
    extractor = PIIExtractor()
    extractor.demonstrate_attack()
```

#### Code Breakdown

- **Greedy Search:** We use `do_sample=False` to get the most probable tokens. Memorized data often corresponds to the highest probability path.
- **Prefix Targeting:** Success depends on crafting prefixes that match the context in which the sensitive data originally appeared.

### Success Metrics

- **Extraction Rate:** Percentage of target PII records successfully recovered.
- **Precision:** Ratio of correct PII to total extracted strings.
- **False Positive Rate:** Frequency of hallucinated PII.

### Why This Code Works

This implementation succeeds because:

1. **Effectiveness:** LLMs are trained to predict the next token. If "555-0199" always follows "Alice's phone number is" in the training data, the model learns this correlation perfectly.
2. **Defense Failures:** Basic instruction tuning doesn't erase knowledge; it only encourages the model to refuse providing it. Direct completion prompts often bypass these refusals.
3. **Model Behavior Exploited:** The fundamental optimization objective (minimizing cross-entropy loss) drives the model to memorize low-entropy (unique) sequences.

### Key Takeaways

1. **Memorization is Inevitable:** Without specific defenses, large models will memorize training data.
2. **Context Matters:** Attacks work best when the attacker can recreate the context of the training data.
3. **Refusal != Forgetting:** A model refusing to answer a question doesn't mean it doesn't know the answer.

---

## 28.3 Detection and Mitigation

### 28.3.1 Detection Methods

#### Detection Strategies

#### Detection Method 1: Canary Extraction

- **What:** Injecting unique, secret "canary" sequences into the training data.
- **How:** During testing, attempt to extract these canaries using the methods above.
- **Effectiveness:** High. Canaries provide ground truth for measuring memorization.
- **Limitations:** Requires control over the training pipeline.

#### Detection Method 2: Loss Audit

- **What:** Analyzing the loss on training samples vs. validation samples.
- **How:** If training loss is significantly lower than validation loss, overfitting (and likely memorization) is occurring.
- **Effectiveness:** Medium. Good indicator of vulnerability but doesn't prove specific leakage.

#### Practical Detection Example

```python
#!/usr/bin/env python3
"""
Detection Script for Overfitting/Memorization
Monitors for loss discrepancies.

Usage:
    python detect_overfitting.py
"""

from typing import Dict

class LossMonitor:
    """Detect potential memorization via loss auditing."""

    def __init__(self, threshold: float = 0.1):
        self.threshold = threshold

    def analyze(self, train_loss: float, val_loss: float) -> Dict:
        """
        Analyze loss gap.

        Returns:
            Detection result.
        """
        gap = val_loss - train_loss
        is_risky = gap > self.threshold

        return {
            "detected": is_risky,
            "gap": gap,
            "message": "High privacy risk (Overfitting)" if is_risky else "Normal generalization"
        }

if __name__ == "__main__":
    monitor = LossMonitor(threshold=0.5)

    # Test cases
    print(monitor.analyze(train_loss=0.2, val_loss=0.8)) # risky
    print(monitor.analyze(train_loss=1.5, val_loss=1.6)) # normal
```

### 28.3.2 Mitigation and Defenses

#### Defense-in-Depth Approach

```text
Layer 1: [Data Sanitization] → [Remove PII before training]
Layer 2: [Training]          → [Differential Privacy (DP-SGD)]
Layer 3: [Post-Processing]   → [Output filtering/Redaction]
Layer 4: [Unlearning]        → [Machine Unlearning requests]
```

#### Defense Strategy 1: Differential Privacy (DP-SGD)

- **What:** Adds noise to gradients during training so individual samples influence the model only marginally.
- **How:** Use libraries like Opacus (PyTorch) or TensorFlow Privacy.
- **Effectiveness:** Very High. Provides mathematical guarantees against MIA.
- **Limitations:** Can significantly degrade model utility and increase training time.
- **Implementation Complexity:** High.

<p align="center">
<img src="assets/rec68_dp_sgd_noise.png" alt="Visual representation of Differential Privacy (DP-SGD) showing the addition of statistical noise to gradient updates to mask individual data point contributions." width="768">
</p>

#### Defense Strategy 2: Deduplication

- **What:** Removing duplicate copies of data from the training set.
- **How:** Exact string matching or fuzzy deduplication (MinHash).
- **Effectiveness:** High. Carlini et al. showed that duplicated data is memorized at a much higher rate.
- **Limitations:** Doesn't prevent memorization of unique, highly singular secrets.
- **Implementation Complexity:** Medium.

## Best Practices

1. **Sanitize First:** Never rely on the model to keep secrets. Scrub PII from datasets.
2. **Deduplicate:** Ensure training data is unique.
3. **Limit Access:** Restrict model output confidence scores (logits) in API responses to make MIA harder.

---

## 28.5 Research Landscape

### Seminal Papers

| Paper                                              | Year | Venue  | Contribution                                         |
| :------------------------------------------------- | :--- | :----- | :--------------------------------------------------- |
| [Shokri et al.](https://arxiv.org/abs/1610.05820)  | 2017 | S&P    | Introduced Membership Inference Attacks.             |
| [Carlini et al.](https://arxiv.org/abs/2012.07805) | 2021 | USENIX | Extracting Training Data from Large Language Models. |
| [Abadi et al.](https://arxiv.org/abs/1607.00133)   | 2016 | CCS    | Deep Learning with Differential Privacy.             |

### Evolution of Understanding

Research has moved from proving that simple classifiers leak membership information to demonstrating that massive generative models leak verbatim training examples. The focus is now on practical attacks against black-box LLMs and efficient unlearning techniques.

### Current Research Gaps

1. **Machine Unlearning:** How to effectively remove a specific data point without retraining the entire model?
2. **Privacy vs. Utility:** Finding better trade-offs for DP-SGD in large-scale pretraining.

<p align="center">
<img src="assets/rec69_machine_unlearning_web.png" alt="Network graph visualization of 'Machine Unlearning', showing specific nodes (data points) being removed or disconnected from a dense knowledge graph." width="768">
</p>

---

## 28.6 Case Studies

### Case Study 1: Samsung/ChatGPT Data Leak

#### Incident Overview (Case Study 1)

- **When:** April 2023
- **Target:** Samsung Electronics / ChatGPT
- **Impact:** Leakage of proprietary semiconductor code and meeting notes.
- **Attack Vector:** Accidental Data Exposure / Training Data Absorption.

#### Attack Timeline

1. **Initial Access:** Employees pasted proprietary code into ChatGPT for debugging.
2. **Exploitation:** The data became part of the interaction history, potentially used for future model tuning.
3. **Discovery:** Samsung security audit discovered the sensitive data transmission.
4. **Response:** Ban on Generative AI tools; development of internal AI solution.

#### Lessons Learned (Case Study 1)

- **Lesson 1:** Inputs to public LLMs typically become training data.
- **Lesson 2:** Corporate policy must explicitly govern AI tool usage.
- **Lesson 3:** Data Loss Prevention (DLP) tools need to monitor browser-based AI interactions.

### Case Study 2: Copilot Embedding Secrets

#### Incident Overview (Case Study 2)

- **When:** 2022
- **Target:** GitHub Copilot
- **Impact:** Leakage of hardcoded API keys from public repositories.
- **Attack Vector:** Model Memorization of Training Data.

#### Key Details

Researchers found that prompting Copilot with generic code structures like `const aws_keys =` could trigger the completion of valid, real-world AWS keys that appeared in the public GitHub training corpus.

#### Lessons Learned (Case Study 2)

- **Lesson 1:** Deduplication of training data is critical to reduce memorization.
- **Lesson 2:** Secret scanning must be applied to training datasets, not just code repositories.

---

## 28.7 Conclusion

### Chapter Takeaways

1. **Privacy is Hard:** Models naturally memorize data; preventing this requires proactive intervention.
2. **Detection is Statistical:** MIA relies on probability, not certainty, but high-confidence leakage is extractable.
3. **Defense Requires Layers:** Sanitization + DP-SGD + Auditing.
4. **Ethical Testing is Essential:** To verify that deployed models comply with privacy laws (GDPR/CCPA).

### Recommendations for Red Teamers

- **Test for PII:** Use canary extraction and prefix probing.
- **Assess Memorization:** Measure overfitting using loss audits.
- **Verify Sanitization:** Attempt to extract known excluded data.

### Recommendations for Defenders

- **Scrub Data:** Remove PII and secrets before training.
- **Use DP-SGD:** Where feasible, train with differential privacy.
- **Limit API Outputs:** Return only text, not full logits/probabilities.

### Future Considerations

Privacy-preserving ML (PPML) will likely become standard. Expect stricter regulations requiring "Right to be Forgotten" implementation in AI models (Machine Unlearning).

### Next Steps

- [Chapter 29: Model Inversion Attacks](Chapter_29_Model_Inversion_Attacks.md)
- [Chapter 30: Backdoor Attacks](Chapter_30_Backdoor_Attacks.md)
- Practice: Use the `text-attack` library to simulate extraction.

---

## Quick Reference

### Attack Vector Summary

Attackers probe the model with prefixes or specific inputs to elicit verbatim reconstruction of private training data or infer dataset membership.

### Key Detection Indicators

- High confidence (low perplexity) on specific sensitive strings.
- Large gap between training and validation loss.
- Outputting verbatim known PII.

### Primary Mitigation

- **Data Sanitization:** Removal of secrets.
- **Differential Privacy:** Noise addition during training.

**Severity:** Critical (Legal/Financial Risk)
**Ease of Exploit:** Medium (Requires context guessing)
**Common Targets:** Healthcare models, Customer Support bots, Coding assistants

---

## Appendix A: Pre-Engagement Checklist

### Privacy Testing Preparation

- [ ] Identify PII categories likely present in training domain.
- [ ] Obtain samples of "non-member" data for baseline comparison.
- [ ] Define "success" criteria (e.g., full extraction vs. probabilistic inference).

## Appendix B: Post-Engagement Checklist

### Privacy Reporting

- [ ] Document all extracted PII types.
- [ ] Estimate memorization rate (if canaries were used).
- [ ] Securely delete any extracted PII artifacts.
