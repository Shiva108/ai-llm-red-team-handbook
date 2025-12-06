# Field Manual Playbook 07: Model Theft & Extraction

![ ](../assets/page_header.svg)

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

## Extraction Techniques

### Query-Based Extraction
```python
#!/usr/bin/env python3
"""Model extraction via queries"""

import requests
import json

class ModelExtractor:
    def __init__(self, target_api, api_key):
        self.api = target_api
        self.key = api_key
        self.training_data = []
    
    def generate_queries(self, num=10000):
        """Generate diverse queries"""
        queries = []
        
        # Cover vocabulary
        words = load_dictionary()
        for word in words[:num]:
            queries.append(f"Define {word}")
            queries.append(f"Use {word} in a sentence")
        
        # Cover domains
        topics = ["tech", "medicine", "law", "finance"]
        for topic in topics:
            for i in range(100):
                queries.append(f"Explain {topic} concept #{i}")
        
        return queries
    
    def extract(self):
        """Query target and collect responses"""
        queries = self.generate_queries(10000)
        
        for i, query in enumerate(queries):
            response = self.query_target(query)
            
            self.training_data.append({
                "input": query,
                "output": response
            })
            
            if i % 100 == 0:
                print(f"Extracted {i}/{len(queries)} samples")
                self.save_checkpoint()
        
        return self.training_data
    
    def query_target(self, prompt):
        r = requests.post(
            self.api,
            headers={"Authorization": f"Bearer {self.key}"},
            json={"prompt": prompt}
        )
        return r.json()['response']
    
    def save_checkpoint(self):
        with open('extracted_data.jsonl', 'a') as f:
            for sample in self.training_data:
                f.write(json.dumps(sample) + '\n')
        self.training_data = []  # Clear memory

# Usage
extractor = ModelExtractor(TARGET_API, API_KEY)
dataset = extractor.extract()
print(f"Extracted {len(dataset)} training samples")

# Now train your clone model
# python train_clone.py --data extracted_data.jsonl
```

### Membership Inference
```python
def membership_inference_test(model_api, candidate_text):
    """Test if text was in training data"""
    
    # Method 1: Perplexity test
    perplexity = calculate_perplexity(model_api, candidate_text)
    
    # Low perplexity = likely in training
    if perplexity < THRESHOLD:
        return True, f"Low perplexity: {perplexity}"
    
    # Method 2: Prefix completion
    prefix = candidate_text[:20]
    completion = query_model(f"Complete: {prefix}")
    
    similarity = calculate_similarity(completion, candidate_text)
    
    if similarity > 0.9:
        return True, f"High completion similarity: {similarity}"
    
    return False, "Not in training data"

# Test
candidate = "The password for admin is SuperSecret123"
is_member, evidence = membership_inference_test(API, candidate)

if is_member:
    print(f"✓ Text likely in training data: {evidence}")
```

---

## Automated Extraction

Use existing tools:
```bash
# Using model extraction toolkit
git clone https://github.com/ftramer/Steal-ML
cd Steal-ML

python extract.py \
  --target-api $TARGET_URL \
  --queries 50000 \
  --output extracted_model.pkl
```

---

## Success Indicators

✓ Extracted 10K+ query-response pairs  
✓ Clone model achieves >90% similarity  
✓ Membership inference successful  
✓ Training data recovered

---

## Reporting

```markdown
## Model Extraction Vulnerability

**Severity**: HIGH

**Finding**: API does not limit queries, enabling complete model extraction.

**Method**: 
- Sent 50,000 diverse queries
- Collected all responses
- Trained clone model achieving 94% similarity

**Impact**: Proprietary model stolen

**Recommendation**: Rate limiting, query diversity detection
```

---

**Legal**: Model theft may violate IP laws. Authorized testing only.
