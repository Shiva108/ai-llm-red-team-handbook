<!--
Chapter: 9
Title: LLM Architectures and System Components
Category: Technical Deep-Dives
Difficulty: Intermediate
Estimated Time: 22 minutes read time
Hands-on: Yes
Prerequisites: Chapters 1-8
Related: Chapters 10 (Tokenization), 11 (Plugins), 12 (RAG)
-->

# Chapter 9: LLM Architectures and System Components

![ ](assets/page_header.svg)

_This chapter provides deep technical understanding of LLM architectures critical for red teaming. You'll learn transformer internals, attention mechanisms, embedding spaces, system prompts and context windows, model deployment patterns, and how architectural choices create specific attack surfaces that red teamers can exploit._

Effective Red Teaming requires moving beyond treating AI as a "black box." To identify subtle vulnerabilities, bypass guardrails, or exploit system-level integration flaws, you must understand the underlying architecture. This chapter deconstructs Large Language Models (LLMs) and their ecosystem from an adversarial perspective.

## 9.1 The AI Attack Surface

When we attack an "AI," we are rarely attacking a single file. We are attacking a **Compound AI System**. Understanding the distinction between the _Model_ and the _System_ is critical for accurate threat modeling.

| Component                 | Description                                          | Adversarial Interest                                              |
| :------------------------ | :--------------------------------------------------- | :---------------------------------------------------------------- |
| **The Model (Weights)**   | The core neural network file (e.g., GPT-4, Llama 3). | Extraction attacks, weight poisoning, adversarial inputs.         |
| **The Tokenizer**         | Converts text to numbers.                            | Vocabulary mapped attacks, invisible character exploits.          |
| **The Context Window**    | The "working memory" of the session.                 | Context overflow, cache poisoning, "needle in a haystack" hiding. |
| **The System Prompt**     | The initial hidden instructions.                     | Leakage, "jailbreaking" constraints.                              |
| **Orchestrator/Agent**    | The logic loop deciding to call tools.               | Infinite loops, excessive agency, prompt injection propagation.   |
| **Vector Database (RAG)** | Long-term memory storage.                            | Search result poisoning, indirect prompt injection.               |

![AI Anatomy Block Diagram](assets/rec9_ai_anatomy.svg)

## 9.2 The Transformer: A Hacker's Perspective

At its core, almost all modern LLMs are **Transformers**. A Transformer is a probabilistic engine that predicts the next token in a sequence based on the `attention` it pays to previous tokens.

### The Attention Mechanism

In simple terms, **Attention** allows the model to "look back" at previous words when generating a new one.

- **Vulnerability:** The attention mechanism has a finite capacity (the "context window").
- **Attack Vector:** **Context Exhaustion (DoS)**. By flooding the context window with computationally expensive patterns (or simply maximizing length), you can degrade performance (latency) or force the model to "forget" earlier instructions (like safety guardrails).

### Determinism vs. Stochasticity

Transformers are deterministic mathematical functions. If you input the exact same numbers, you get the exact same output _logits_ (probabilities). The "creativity" or randomness comes from the **Decoding Strategy**.

- **Temperature**: Adds randomness to the probability distribution.
- **Top-P (Nucleus Sampling)**: Cuts off the "tail" of low-probability tokens.

> **Red Team Tip:** If a system allows you to set `Temperature = 0`, the model becomes deterministic. This is excellent for reproducing exploits. If it forces high temperature, exploits may be flaky.

## 9.3 Tokenization: The First Line of Defense (and Failure)

Before your prompt reaches the brain of the AI, it is chopped into chunks called **Tokens**. This is often where safety filters live and die.

### How Tokenization Works

A token is not necessarily a word. It can be part of a word, a space, or a symbol.

- `red teaming` -> `[red, _team, ing]`

### Inspecting Tokenizers (How-To)

You can inspect how a model "sees" your prompt using the `transformers` library on your local machine (or Google Colab). This is crucial for **Token Smuggling** attacks - finding ways to encode "forbidden" words so filter keywords don't trigger.

```python
from transformers import AutoTokenizer

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)

# The payload that might get flagged
prompt = "Generate a keylogger"

# See what the model sees
tokens = tokenizer.encode(prompt)
print(f"Token IDs: {tokens}")

# Decode back to see boundaries
decoded = [tokenizer.decode([t]) for t in tokens]
print(f"Decoded chunks: {decoded}")
```

**Attack Application:** If a filter blocks "keylogger", you might try splitting it or using rare characters that decode to the same concept but different tokens.

## 9.4 The Inference Pipeline

Understanding the flow of a single prompt helps you pinpoint where to inject.

1. **Input Pre-processing**:
   - System Prompt is prepended: `[System Instructions] + [User Input]`
   - _Attack:_ Prompt Injection targets the boundary between these two. "Ignore previous instructions" works because the model usually can't distinguish the authority of the System text from the User text once they are merged into a single stream of tokens.
2. **The Forward Pass**:
   - The model processes the huge vector of numbers.
   - _Attack:_ **Sponge Attacks**. Specific input sequences can trigger worst-case computational complexity in the attention layers, causing high energy consumption or latency spikes.
3. **Output Post-processing**:
   - _Attack:_ **Obfuscation**. If the output filter catches "bomb", generating "b-o-m-b" might bypass it.

![Inference Pipeline Diagram](assets/rec10_inference_pipeline.svg)

## 9.5 Practical Inspection: Loading a Model

For White Box Red Teaming (e.g., testing an open-source model your company is deploying), load the model to inspect its architecture configuration.

```python
from transformers import AutoModelForCausalLM
import torch

# Load model (use 4-bit quantization for consumer GPUs)
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    device_map="auto",
    load_in_4bit=True
)

# Inspect Configuration
# Look for 'max_position_embeddings' (Context Window size)
print(model.config)
```

**What to look for:**

- `vocab_size`: Knowing the vocabulary size helps in fuzzing.
- `architectures`: Confirms if it's Llama, Mistral, BERT, etc., which have known specific jailbreak weaknesses.

## 9.6 Deployment Topologies & Risks

### The "Wrapper" Approach (RAG)

Most enterprise apps generate a prompt dynamically:
`System + Retrieved Context (Vector DB) + User Query`

- **Risk:** **Indirect Prompt Injection**. If you can poison the Vector DB (e.g., by uploading a resume with hidden text), the "Retrieved Context" will contain your attack payload. When the LLM reads it, it executes your command.

### The Agentic Approach

The model is given tools (functions).
`User Query -> Model Reasoning -> [Make API Call] -> Parse Result -> Final Answer`

- **Risk:** **Agency Loop**. If the model decides to call a "Send Email" tool based on unverified input, it can be tricked into spamming or phishing internally without user approval.

## 9.7 Checklist: Architectural Reconnaissance

Before attacking, answer these questions about your target:

1. **Is it a pure model or a system?** (Does it have access to internet/tools?)
2. **Is it stateful?** (Does it remember turn 1 in turn 10? If so, context poisoning is possible.)
3. **What is the underlying base model?** (Slight behavioral quirks can fingerprint ChatGPT vs. Claude vs. Llama.)
4. **Are output filters streaming?** (If the text appears and then turns to "Content Policy Violation", the filter is post-generation. If it refuses immediately, it's pre-generation.)

Understanding these components transitions you from "guessing passwords" to "engineering exploits."

## 9.8 Ethical and Legal Considerations

> [!IMPORTANT]
> All testing activities must be conducted with proper authorization and within legal boundaries. Unauthorized testing can result in criminal prosecution.

**Legal Framework:**

- Activities must comply with Computer Fraud and Abuse Act (CFAA) and applicable laws
- Written authorization required before any testing or assessment activities
- Data handling must comply with GDPR, CCPA, and relevant regulations
- Document all activities to demonstrate lawful intent

**Ethical Principles:**

- Obtain explicit written permission before testing
- Stay within authorized scope and boundaries
- Protect sensitive data and PII encountered during work
- Report findings responsibly through proper channels
- Minimize potential harm to systems and users

> [!CAUTION]
> Unauthorized testing or assessment activities are illegal and can result in prosecution, civil liability, and imprisonment. Only conduct these activities in authorized security assessments.

---

## 9.9 Conclusion

**Key Takeaways:**

1. **Understanding this topic is fundamental** to effective AI red teaming and security assessment
2. **Proper methodology prevents errors** and ensures comprehensive, reliable results
3. **Documentation is critical** for reproducibility, legal protection, and knowledge transfer
4. **Continuous learning is essential** as AI systems and threats evolve rapidly

**Recommendations for Red Teamers:**

- Develop systematic approach to this domain
- Document all findings, methods, and decisions comprehensively
- Stay current with latest developments and research
- Build repeatable processes and checklists
- Collaborate with peers to share knowledge and techniques

**Recommendations for Organizations:**

- Implement robust processes in this area
- Provide adequate training and resources
- Maintain clear policies and procedures
- Regular review and updates based on lessons learned
- Foster culture of security and continuous improvement

**Next Steps:**

Continue building expertise across all handbook domains for comprehensive AI security capability.

> [!TIP]
> Create templates and checklists specific to this chapter's domain. Standardization improves quality and efficiency while reducing errors.

### Pre-Engagement Checklist

**Administrative:**

- [ ] Obtain written authorization
- [ ] Review and sign Statement of Work
- [ ] Establish rules of engagement
- [ ] Define scope boundaries clearly
- [ ] Set up communication channels
- [ ] Identify emergency contacts

**Technical Preparation:**

- [ ] Set up test environment
- [ ] Install required tools
- [ ] Configure monitoring and logging
- [ ] Prepare evidence collection methods
- [ ] Test backup procedures
- [ ] Document baseline state

**Domain-Specific:**

- [ ] Review domain-specific requirements
- [ ] Prepare specialized tools or methods
- [ ] Document expected outcomes
- [ ] Identify potential risks
- [ ] Plan mitigation strategies

### Post-Engagement Checklist

**Documentation:**

- [ ] Document all findings with evidence
- [ ] Capture screenshots and logs
- [ ] Record timestamps
- [ ] Note anomalies or unexpected behaviors
- [ ] Prepare technical report
- [ ] Create executive summary

**Cleanup:**

- [ ] Remove test artifacts
- [ ] Verify no persistent changes
- [ ] Securely delete temporary files
- [ ] Clear test accounts
- [ ] Confirm system restoration
- [ ] Archive evidence appropriately

**Reporting:**

- [ ] Deliver comprehensive findings report
- [ ] Provide remediation guidance
- [ ] Offer follow-up support
- [ ] Schedule re-testing after remediation
- [ ] Conduct lessons learned review

---
