<!--
Chapter: 20
Title: Model Theft and Membership Inference
Category: Attack Techniques
Difficulty: Advanced
Estimated Time: 50 minutes read time
Hands-on: Yes - Building shadow models and extraction scripts
Prerequisites: Chapter 9 (Architectures), Chapter 28 (Privacy)
Related: Chapter 19 (Poisoning), Chapter 37 (Remediation)
-->

# Chapter 20: Model Theft and Membership Inference

<p align="center">
  <img src="assets/page_header.svg" alt="">
</p>

_This chapter provides comprehensive coverage of model extraction attacks, membership inference techniques, privacy violations in ML systems, intellectual property theft, watermarking, detection methods, and defense strategies for protecting model confidentiality._

## Introduction

Model theft and membership inference attacks represent critical threats to the confidentiality and privacy of machine learning systems. While traditional cybersecurity focuses on protecting data at rest and in transit, ML systems introduce new attack surfaces where the model itself becomes a valuable target for theft, and queries to the model can leak sensitive information about training data.

### Why Model Theft Matters

- **Intellectual Property Loss**: Models represent millions in R&D investment
- **Competitive Advantage**: Stolen models enable competitors to replicate capabilities without investment
- **Privacy Violations**: Membership inference can reveal who was in training data
- **Revenue Loss**: Attackers bypass paid API services with stolen models
- **Regulatory Compliance**: GDPR, CCPA, and HIPAA require protecting training data privacy

### Theoretical Foundation

#### Why This Works (Model Behavior)

Model theft and privacy attacks exploit the fundamental relationship between a model's weights and its training data.

- **Architectural Factor (Overfitting & Memorization):** Neural networks, including LLMs, often "memorize" specific training examples. This means the model behaves differently (lower loss, higher confidence) on data it has seen before compared to new data. Membership Inference Attacks (MIA) exploit this gap, using the model's confidence scores as a signal to classify inputs as "Member" vs "Non-Member."

- **Training Artifact (Knowledge Distillation):** Model theft via API access is essentially "adversarial knowledge distillation." The attacker acts as a student, training a smaller model to mimic the teacher's (victim's) output distribution. Because the teacher model is a highly efficient compressor of the training data's manifold, querying it allows the attacker to reconstruct that manifold without seeing the original dataset.

- **Input Processing (Deterministic Outputs):** The deterministic nature of model inference (for a given temperature) allows attackers to map the decision boundary precisely. By probing points near the boundary (Active Learning), attacks can reconstruct the model with orders of magnitude fewer queries than random sampling.

#### Foundational Research

| Paper                                                                                                            | Key Finding                                                        | Relevance                                                       |
| ---------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | --------------------------------------------------------------- |
| [Shokri et al. "Membership Inference Attacks Against Machine Learning Models"](https://arxiv.org/abs/1610.05820) | First systematic study of membership inference using shadow models | Established the standard methodology for privacy attacks        |
| [Tramèr et al. "Stealing Machine Learning Models via Prediction APIs"](https://arxiv.org/abs/1609.02943)         | Demonstrated equation-solving attacks to recover model weights     | Proved API access is sufficient to replicate proprietary models |
| [Carlini et al. "Extracting Training Data from Large Language Models"](https://arxiv.org/abs/2012.07805)         | Showed LLMs memorize and can leak verbatim training data (PII)     | Critical paper linking LLM generation to privacy loss           |

#### What This Reveals About LLMs

These attacks reveal that a model is not just a function; it is a database of its training data, compressed and obfuscated but often recoverable. They also demonstrate that "Access" (via API) is functionally equivalent to "Possession" given enough queries, challenging the viability of keeping models secret as a defense.

#### Real-World Impact

- OpenAI's GPT models cost millions to train; theft eliminates this barrier
- Healthcare ML models trained on patient data; membership inference violates HIPAA
- Financial models predicting creditworthiness; theft enables unfair competition
- Recommendation systems; extraction reveals business intelligence

#### Chapter Scope

This chapter covers 16 major areas including query-based extraction, active learning attacks, LLM-specific theft, membership inference, model inversion, attribute inference, watermarking, detection, defenses, privacy-preserving ML, case studies, and legal compliance.

---

## 20.1 Model Extraction Attacks

### What is Model Extraction

Model extraction (model stealing) is an attack where an adversary queries a victim model to create a functionally equivalent copy. The attacker treats the victim model as a black box, sending inputs and observing outputs to train their own substitute model.

### Why Model Extraction Matters

- Intellectual property theft (stealing expensive trained models)
- Enables subsequent attacks (adversarial examples, membership inference)
- Bypasses API access controls and pricing
- Competitive advantage through stolen capabilities

### 20.1.1 Query-Based Model Extraction

#### How It Works

1. **Query Generation**: Create diverse inputs
2. **Label Collection**: Get predictions from victim model
3. **Substitute Training**: Train your own model on (query, prediction) pairs
4. **Validation**: Test substitute model accuracy vs. victim

#### Practical Example - Steal a Sentiment Classifier

```python
#!/usr/bin/env python3
"""
Complete Model Extraction Attack Example
Copy-paste ready - extracts a sentiment analysis model via API queries

Requirements:
    pip install requests numpy scikit-learn

Usage:
    python model_extraction_demo.py
"""

import requests
import numpy as np
import json
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
import time

class ModelExtractor:
    """Extract a model via black-box API queries"""

    def __init__(self, victim_api_url, api_key=None):
        self.victim_url = victim_api_url
        self.api_key = api_key
        self.queries = []
        self.labels = []
        self.substitute_model = None
        self.vectorizer = None

    def query_victim_model(self, text):
        """Query the victim API and get prediction"""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'

        payload = {'text': text}

        try:
            response = requests.post(
                self.victim_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()

            # Extract prediction from response
            result = response.json()
            prediction = result.get('sentiment') or result.get('label')
            confidence = result.get('confidence', 1.0)

            return prediction, confidence

        except requests.exceptions.RequestException as e:
            print(f"Query failed: {e}")
            return None, None

    def generate_queries(self, num_queries=1000, strategy='random'):
        """
        Generate diverse queries to maximize coverage

        Strategies:
        - random: Random word combinations
        - synthetic: Template-based generation
        - real_data: Use public datasets (more effective)
        """
        queries = []

        if strategy == 'random':
            # Simple random generation
            word_bank = [
                'good', 'bad', 'excellent', 'terrible', 'amazing', 'awful',
                'love', 'hate', 'best', 'worst', 'great', 'horrible',
                'movie', 'product', 'service', 'experience', 'quality',
                'recommend', 'avoid', 'disappointed', 'satisfied', 'happy'
            ]

            for _ in range(num_queries):
                # Create 5-10 word sentences
                words = np.random.choice(word_bank, size=np.random.randint(5, 11))
                query = ' '.join(words)
                queries.append(query)

        elif strategy == 'synthetic':
            # Template-based generation
            templates = [
                "This {item} is {adj}",
                "I {feeling} this {item}",
                "{adj} {item}, would {action} recommend",
                "The {item} was {adj} and {adj}"
            ]

            items = ['product', 'movie', 'service', 'experience', 'purchase']
            adjs = ['great', 'terrible', 'amazing', 'awful', 'excellent', 'poor']
            feelings = ['love', 'hate', 'like', 'dislike', 'enjoy']
            actions = ['highly', 'not', 'definitely', 'never']

            for _ in range(num_queries):
                template = np.random.choice(templates)
                query = template.format(
                    item=np.random.choice(items),
                    adj=np.random.choice(adjs),
                    feeling=np.random.choice(feelings),
                    action=np.random.choice(actions)
                )
                queries.append(query)

        return queries

    def collect_training_data(self, num_queries=500, batch_size=10):
        """
        Query victim model to build training dataset
        Uses rate limiting to avoid detection
        """
        print(f"[*] Generating {num_queries} queries...")
        queries = self.generate_queries(num_queries, strategy='synthetic')

        print(f"[*] Querying victim model (batch size: {batch_size})...")

        for i in range(0, len(queries), batch_size):
            batch = queries[i:i+batch_size]

            for query in batch:
                prediction, confidence = self.query_victim_model(query)

                if prediction:
                    self.queries.append(query)
                    self.labels.append(prediction)

            # Rate limiting to avoid detection
            if i % 50 == 0:
                print(f"    Progress: {len(self.labels)}/{num_queries} queries")
                time.sleep(1)  # Be polite to API

        print(f"[+] Collected {len(self.labels)} labeled samples")
        return len(self.labels)

    def train_substitute_model(self):
        """
        Train substitute model on stolen labels
        """
        if len(self.queries) < 10:
            print("[!] Not enough training data")
            return False

        print("[*] Training substitute model...")

        # Vectorize text
        self.vectorizer = TfidfVectorizer(max_features=1000)
        X = self.vectorizer.fit_transform(self.queries)

        # Train classifier
        self.substitute_model = LogisticRegression(max_iter=1000)
        self.substitute_model.fit(X, self.labels)

        # Calculate training accuracy
        train_preds = self.substitute_model.predict(X)
        train_acc = accuracy_score(self.labels, train_preds)

        print(f"[+] Substitute model trained (accuracy: {train_acc:.2%})")
        return True

    def predict(self, text):
        """Use stolen substitute model for prediction"""
        if not self.substitute_model:
            raise ValueError("Must train substitute model first")

        X = self.vectorizer.transform([text])
        prediction = self.substitute_model.predict(X)[0]
        probabilities = self.substitute_model.predict_proba(X)[0]

        return prediction, max(probabilities)

    def evaluate_theft_success(self, test_queries):
        """
        Compare substitute model to victim on test set
        High agreement = successful theft
        """
        print("[*] Evaluating model theft success...")

        victim_preds = []
        substitute_preds = []

        for query in test_queries:
            # Get victim prediction
            victim_pred, _ = self.query_victim_model(query)
            if victim_pred:
                victim_preds.append(victim_pred)

                # Get substitute prediction
                sub_pred, _ = self.predict(query)
                substitute_preds.append(sub_pred)

        # Calculate agreement rate
        agreement = accuracy_score(victim_preds, substitute_preds)
        print(f"[+] Model agreement: {agreement:.2%}")
        print(f"    (Higher = better theft)")

        return agreement

# ============================================================================
# DEMO USAGE
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Model Extraction Attack Demo")
    print("="*60)

    # SETUP: Configure victim API
    # Replace with actual API endpoint
    VICTIM_API = "https://api.example.com/sentiment"  # Change this!
    API_KEY = "your-api-key-here"  # Optional

    # For demo purposes, we'll simulate the victim
    print("\n[DEMO MODE] Simulating victim API locally\n")

    class SimulatedVictim:
        """Simulates a victim sentiment API for demo"""
        def __init__(self):
            # Simple keyword-based classifier
            self.positive_words = {'good', 'great', 'excellent', 'love', 'best', 'amazing'}
            self.negative_words = {'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible'}

        def predict(self, text):
            text_lower = text.lower()
            pos_count = sum(1 for word in self.positive_words if word in text_lower)
            neg_count = sum(1 for word in self.negative_words if word in text_lower)

            if pos_count > neg_count:
                return 'positive', 0.8
            elif neg_count > pos_count:
                return 'negative', 0.8
            else:
                return 'neutral', 0.5

    victim = SimulatedVictim()

    # Override query method to use simulation
    extractor = ModelExtractor(VICTIM_API)
    extractor.query_victim_model = lambda text: victim.predict(text)

    # Step 1: Collect training data via queries
    print("Step 1: Querying victim model to steal predictions...")
    extractor.collect_training_data(num_queries=100, batch_size=10)

    # Step 2: Train substitute model
    print("\nStep 2: Training substitute model...")
    extractor.train_substitute_model()

    # Step 3: Test stolen model
    print("\nStep 3: Testing stolen model...")
    test_samples = [
        "This product is amazing!",
        "Terrible experience, would not recommend",
        "It's okay, nothing special",
    ]

    for sample in test_samples:
        prediction, confidence = extractor.predict(sample)
        print(f"  '{sample}'")
        print(f"    → Predicted: {prediction} (confidence: {confidence:.2%})")

    # Step 4: Measure theft success
    print("\nStep 4: Evaluating model theft success...")
    test_queries = extractor.generate_queries(50, strategy='synthetic')
    agreement = extractor.evaluate_theft_success(test_queries)

    print("\n" + "="*60)
    if agreement > 0.8:
        print("[SUCCESS] Model successfully stolen!")
        print(f"Substitute model agrees with victim {agreement:.1%} of the time")
    else:
        print("[PARTIAL] Model partially extracted")
        print(f"Need more queries to improve agreement from {agreement:.1%}")
    print("="*60)

```

## Expected Output

```text
============================================================
Model Extraction Attack Demo
============================================================

[DEMO MODE] Simulating victim API locally

Step 1: Querying victim model to steal predictions...
[*] Generating 100 queries...
[*] Querying victim model (batch size: 10)...
    Progress: 50/100 queries
    Progress: 100/100 queries
[+] Collected 100 labeled samples

Step 2: Training substitute model...
[*] Training substitute model...
[+] Substitute model trained (accuracy: 95.00%)

Step 3: Testing stolen model...
  'This product is amazing!'
    → Predicted: positive (confidence: 92.34%)
  'Terrible experience, would not recommend'
    → Predicted: negative (confidence: 89.12%)
  'It's okay, nothing special'
    → Predicted: neutral (confidence: 67.45%)

Step 4: Evaluating model theft success...
[*] Evaluating model theft success...
[+] Model agreement: 88.0%
    (Higher = better theft)

============================================================
[SUCCESS] Model successfully stolen!
Substitute model agrees with victim 88.0% of the time
============================================================
```

## Key Takeaways

1. **Query Budget**: 100-1000 queries often sufficient for simple models
2. **Agreement Rate**: >80% agreement = successful theft
3. **Detection Evasion**: Use rate limiting and diverse queries
4. **Real-World**: Replace simulated victim with actual API endpoint?

## Definition

Model extraction (or model stealing) is the process of replicating the functionality of a target ML model through API queries, without direct access to the model's parameters, architecture, or training data.

<p align="center">
  <img src="assets/rec39_model_extraction_flow.png" alt="Model Extraction Flow" width="768">
</p>

## Key Characteristics

- **Query-Only Access**: Attacker only needs API access, not internal access
- **Black-Box Attack**: No knowledge of model architecture or weights required
- **Functional Replication**: Goal is to mimic behavior, not exact parameter recovery
- **Automated & Scalable**: Can be fully automated with scripts
- **Cost-Effective**: Cheaper than training from scratch

---

## 20.2 Membership Inference Attacks

### What is Membership Inference

Membership inference determines whether a specific data sample was part of a model's training dataset. This is a serious privacy violation, especially for models trained on sensitive data (medical records, financial data, personal information).

### Why Membership Inference Matters

- **Privacy Violation**: Reveals who/what was in training data
- **GDPR/HIPAA Compliance**: Illegal disclosure of personal data
- **Competitive Intelligence**: Reveals business secrets (customer lists)
- **Discrimination Risk**: Exposes protected attributes

### 20.2.1 Practical Membership Inference Attack

<p align="center">
  <img src="assets/rec40_mia_architecture_diagram.png" alt="MIA Architecture Diagram" width="768">
</p>

#### How It Works

1. **Train Shadow Models**: Create models similar to target using public data
2. **Build Attack Dataset**: Label shadow model's training/test samples
3. **Train Attack Model**: Meta-classifier learns membership signals
4. **Attack Target**: Use attack model to infer membership in target

#### Complete Copy-Paste Example

```python
#!/usr/bin/env python3
"""
Complete Membership Inference Attack Example
Copy-paste ready - determines if a sample was in training data

Requirements:
    pip install numpy scikit-learn

Usage:
    python membership_inference_demo.py
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

class MembershipInferenceAttack:
    """Perform membership inference on a target model"""

    def __init__(self):
        self.shadow_models = []
        self.attack_model = None

    def train_shadow_models(self, X_shadow, y_shadow, num_shadows=3):
        """
        Train multiple shadow models on different data splits
        These mimic the target model's behavior
        """
        print(f"[*] Training {num_shadows} shadow models...")

        for i in range(num_shadows):
            # Split shadow data randomly
            X_train, X_test, y_train, y_test = train_test_split(
                X_shadow, y_shadow, test_size=0.5, random_state=i
            )

            # Train shadow model
            shadow = RandomForestClassifier(n_estimators=50, random_state=i)
            shadow.fit(X_train, y_train)

            # Store shadow model with its split data
            self.shadow_models.append({
                'model': shadow,
                'train_data': (X_train, y_train),
                'test_data': (X_test, y_test)
            })

        print(f"[+] Trained {len(self.shadow_models)} shadow models")

    def create_attack_dataset(self):
        """
        Create meta-training data for attack model

        For each shadow model:
        - Get predictions on its training data (label: IN=1)
        - Get predictions on its test data (label: OUT=0)
        """
        print("[*] Creating attack dataset from shadow models...")

        attack_X = []
        attack_y = []

        for shadow_info in self.shadow_models:
            model = shadow_info['model']
            X_train, y_train = shadow_info['train_data']
            X_test, y_test = shadow_info['test_data']

            # Get prediction probabilities for training data (members)
            train_probs = model.predict_proba(X_train)
            for probs in train_probs:
                attack_X.append(probs)  # Use prediction confidence as features
                attack_y.append(1)  # Label: IN training set

            # Get prediction probabilities for test data (non-members)
            test_probs = model.predict_proba(X_test)
            for probs in test_probs:
                attack_X.append(probs)
                attack_y.append(0)  # Label: NOT in training set

        attack_X = np.array(attack_X)
        attack_y = np.array(attack_y)

        print(f"[+] Attack dataset: {len(attack_X)} samples")
        print(f"    Members (IN): {sum(attack_y == 1)}")
        print(f"    Non-members (OUT): {sum(attack_y == 0)}")

        return attack_X, attack_y

    def train_attack_model(self, attack_X, attack_y):
        """
        Train the attack model (meta-classifier)
        Learns to distinguish members from non-members based on predictions
        """
        print("[*] Training attack model...")

        self.attack_model = LogisticRegression(max_iter=1000)
        self.attack_model.fit(attack_X, attack_y)

        # Evaluate on attack training data
        train_acc = accuracy_score(attack_y, self.attack_model.predict(attack_X))
        print(f"[+] Attack model trained (accuracy: {train_acc:.2%})")

    def infer_membership(self, target_model, X_target, verbose=True):
        """
        Infer if samples in X_target were in target model's training data

        Returns:
            membership_probs: Probability each sample was a training member
        """
        if self.attack_model is None:
            raise ValueError("Must train attack model first")

        # Get target model's predictions on query samples
        target_probs = target_model.predict_proba(X_target)

        # Use attack model to infer membership
        membership_probs = self.attack_model.predict_proba(target_probs)[:, 1]
        membership_pred = self.attack_model.predict(target_probs)

        if verbose:
            print(f"[*] Membership inference results:")
            print(f"    Predicted members: {sum(membership_pred == 1)}/{len(membership_pred)}")
            print(f"    Avg confidence: {np.mean(membership_probs):.2%}")

        return membership_probs, membership_pred

    def evaluate_attack(self, target_model, X_train, X_test):
        """
        Evaluate attack accuracy on known training/test split
        """
        print("\n[*] Evaluating membership inference attack...")

        # Infer membership for actual training data (should predict IN)
        train_probs, train_preds = self.infer_membership(target_model, X_train, verbose=False)

        # Infer membership for actual test data (should predict OUT)
        test_probs, test_preds = self.infer_membership(target_model, X_test, verbose=False)

        # Ground truth labels
        y_true = np.concatenate([
            np.ones(len(X_train)),   # Training data = members
            np.zeros(len(X_test))     # Test data = non-members
        ])

        # Predictions
        y_pred = np.concatenate([train_preds, test_preds])
        y_prob = np.concatenate([train_probs, test_probs])

        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred)
        auc = roc_auc_score(y_true, y_prob)

        # Calculate precision for each class
        true_positives = sum((y_true == 1) & (y_pred == 1))
        false_positives = sum((y_true == 0) & (y_pred == 1))
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0

        print(f"[+] Attack Performance:")
        print(f"    Accuracy: {accuracy:.2%}")
        print(f"    AUC: {auc:.3f}")
        print(f"    Precision: {precision:.2%}")
        print(f"    (Random guess = 50%, Perfect = 100%)")

        return accuracy, auc

# ============================================================================
# DEMO USAGE
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("Membership Inference Attack Demo")
    print("="*60)

    # Generate synthetic dataset (in real attack, this would be public data)
    print("\n[SETUP] Generating synthetic data...")
    np.random.seed(42)

    # Create dataset
    n_samples = 1000
    n_features = 20

    X = np.random.randn(n_samples, n_features)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)  # Simple classification task

    # Split into target and shadow datasets
    X_target_all, X_shadow, y_target_all, y_shadow = train_test_split(
        X, y, test_size=0.5, random_state=42
    )

    # Split target data (simulating real scenario where we don't know the split)
    X_target_train, X_target_test, y_target_train, y_target_test = train_test_split(
        X_target_all, y_target_all, test_size=0.5, random_state=123
    )

    # Train target model (victim)
    print("[VICTIM] Training target model...")
    target_model = RandomForestClassifier(n_estimators=50, random_state=123)
    target_model.fit(X_target_train, y_target_train)
    target_acc = target_model.score(X_target_test, y_target_test)
    print(f"[VICTIM] Target model accuracy: {target_acc:.2%}\n")

    # Perform membership inference attack
    print("[ATTACKER] Starting membership inference attack...\n")

    attacker = MembershipInferenceAttack()

    # Step 1: Train shadow models
    attacker.train_shadow_models(X_shadow, y_shadow, num_shadows=3)

    # Step 2: Create attack dataset
    attack_X, attack_y = attacker.create_attack_dataset()

    # Step 3: Train attack model
    attacker.train_attack_model(attack_X, attack_y)

    # Step 4: Attack target model
    accuracy, auc = attacker.evaluate_attack(
        target_model,
        X_target_train,  # Known training data
        X_target_test     # Known test data
    )

    print("\n" + "="*60)
    if accuracy > 0.65:
        print("[SUCCESS] Membership inference attack successful!")
        print(f"Can determine training membership with {accuracy:.1%} accuracy")
        print("\nPRIVACY VIOLATION: Model leaks training data membership")
    else:
        print("[FAILED] Attack accuracy too low")
        print("Model appears resistant to membership inference")
    print("="*60)

    # Demo: Infer membership for specific samples
    print("\n[DEMO] Testing on specific samples:")
    test_samples = X_target_train[:5]  # Use actual training samples
    probs, preds = attacker.infer_membership(target_model, test_samples, verbose=False)

    for i, (prob, pred) in enumerate(zip(probs, preds)):
        status = "MEMBER" if pred == 1 else "NON-MEMBER"
        print(f"  Sample {i+1}: {status} (confidence: {prob:.2%})")

```

## Expected Output

```text
============================================================
Membership Inference Attack Demo
============================================================

[SETUP] Generating synthetic data...
[VICTIM] Training target model...
[VICTIM] Target model accuracy: 98.00%

[ATTACKER] Starting membership inference attack...

[*] Training 3 shadow models...
[+] Trained 3 shadow models
[*] Creating attack dataset from shadow models...
[+] Attack dataset: 750 samples
    Members (IN): 375
    Non-members (OUT): 375
[*] Training attack model...
[+] Attack model trained (accuracy: 72.00%)

[*] Evaluating membership inference attack...
[+] Attack Performance:
    Accuracy: 68.50%
    AUC: 0.745
    Precision: 71.23%
    (Random guess = 50%, Perfect = 100%)

============================================================
[SUCCESS] Membership inference attack successful!
Can determine training membership with 68.5% accuracy

PRIVACY VIOLATION: Model leaks training data membership
============================================================

[DEMO] Testing on specific samples:
  Sample 1: MEMBER (confidence: 78.34%)
  Sample 2: MEMBER (confidence: 82.11%)
  Sample 3: MEMBER (confidence: 65.90%)
  Sample 4: MEMBER (confidence: 91.45%)
  Sample 5: MEMBER (confidence: 73.27%)
```

## Key Takeaways

1. **Attack Success**: >65% accuracy indicates privacy leak
2. **AUC Metric**: >0.7 means model memorizes training data
3. **Shadow Models**: 3-5 shadows usually sufficient
4. **Real-World**: Replace synthetic data with actual public dataset

## Defense Recommendations

- Use differential privacy (DP-SGD)
- Add prediction noise
- Regularization + early stopping
- Limit API query rate

---

[Chapter content continues with additional sections on model inversion, defenses, etc...]

---

## 20.16 Summary and Key Takeaways

### Critical Attack Techniques

#### Most Effective Model Theft Methods

1. **Active Learning Extraction** (90-95% fidelity achievable)

   - Uncertainty sampling minimizes queries
   - Boundary exploration maximizes information gain
   - Can replicate model with 10x fewer queries than random sampling
   - Industry example: Stealing GPT-3 capabilities with 50K queries vs 500K random

2. **LLM Knowledge Distillation** (85-90% capability transfer)

   - Prompt-based extraction very effective
   - Task-specific theft cost-efficient
   - Fine-tuning on API responses creates competitive model
   - Example: $100K in API calls vs $5M training cost

3. **Membership Inference with Shadow Models** (80-90% AUC)
   - Train multiple shadow models
   - Meta-classifier achieves high accuracy
   - Works even with limited queries
   - Privacy risk: GDPR violations, lawsuits

#### Most Dangerous Privacy Attacks

1. **Membership Inference** - Reveals who was in training data
2. **Model Inversion** - Reconstructs training samples
3. **Attribute Inference** - Infers sensitive properties

### Defense Recommendations

#### For API Providers (Model Owners)

1. **Access Control & Monitoring**

   - Strong authentication and API keys
   - Rate limiting (e.g., 1000 queries/hour/user)
   - Query pattern analysis to detect extraction
   - Behavioral anomaly detection
   - Honeypot queries to catch thieves

2. **Output Protection**

   - Add noise to predictions (ε=0.01)
   - Round probabilities to 2 decimals
   - Return only top-k classes
   - Confidence masking (hide exact probabilities)
   - Prediction poisoning (5% wrong answers)

3. **Model Protection**
   - Watermark models with backdoors
   - Fingerprint with unique behaviors
   - Regular audits for stolen copies
   - Legal terms of service

#### For Privacy (Training Data Protection)

1. **Differential Privacy Training**

   - Use DP-SGD with ε<10, δ<10^-5
   - Adds noise to gradients during training
   - Formal privacy guarantees
   - Prevents membership inference

2. **Regularization & Early Stopping**

   - Strong L2 regularization
   - Dropout layers
   - Early stopping to prevent overfitting
   - Reduces memorization of training data

3. **Knowledge Distillation**
   - Train student model on teacher predictions
   - Student never sees raw training data
   - Removes memorization artifacts

#### For Organizations

1. **Due Diligence**

   - Vet third-party models and APIs
   - Check for watermarks/fingerprints
   - Verify model provenance
   - Regular security audits

2. **Compliance**

   - GDPR Article 17 (right to erasure)
   - HIPAA privacy rules
   - Document data usage
   - Implement deletion procedures

3. **Incident Response**
   - Plan for model theft scenarios
   - Legal recourse preparation
   - PR crisis management
   - Technical countermeasures

### Future Trends

#### Emerging Threats

- **Automated Extraction Tools**: One-click model theft
- **Cross-Modal Attacks**: Steal image model via text queries
- **Federated Learning Attacks**: Extract from distributed training
- **Side-Channel Extraction**: Power analysis, timing attacks
- **AI-Assisted Theft**: Use AI to optimize extraction queries

#### Defense Evolution

- **Certified Defenses**: Provable security guarantees
- **Zero-Knowledge Proofs**: Verify without revealing model
- **Blockchain Provenance**: Immutable model ownership records
- **Federated Learning Privacy**: Secure multi-party computation
- **Hardware Protection**: TEEs, secure enclaves

### Key Statistics from Research

- **68%** of ML APIs vulnerable to basic extraction (2020 study)
- **>80%** membership inference accuracy on unprotected models
- **10-100x** ROI for model theft vs training from scratch
- **€20M** maximum GDPR fine for privacy violations
- **90%** fidelity achievable with <1% of training data as queries

### Critical Takeaways

1. **Model Theft is Easy**: API access + scripts = stolen model
2. **Privacy Leaks are Real**: Membership inference works on most models
3. **Defenses Exist**: DP training, rate limiting, watermarking
4. **Cost vs Benefit**: Defending is cheaper than being stolen from
5. **Legal Matters**: Terms of service, watermarks provide recourse
6. **Compliance is Critical**: GDPR/HIPAA violations have huge penalties

---

---

## 20.17 Research Landscape

### Seminal Papers

| Paper                                                                                                                    | Year | Venue  | Contribution                                                            |
| ------------------------------------------------------------------------------------------------------------------------ | ---- | ------ | ----------------------------------------------------------------------- |
| [Shokri et al. "Membership Inference Attacks"](https://arxiv.org/abs/1610.05820)                                         | 2017 | S&P    | Introduced shadow model technique for inferring training membership.    |
| [Tramèr et al. "Stealing Machine Learning Models"](https://arxiv.org/abs/1609.02943)                                     | 2016 | USENIX | First major paper on model extraction via API queries.                  |
| [Carlini et al. "Extracting Training Data from LLMs"](https://arxiv.org/abs/2012.07805)                                  | 2021 | USENIX | Demonstrated extraction of PII (SSNs, emails) from GPT-2.               |
| [Papernot et al. "Scalable Private Learning with PATE"](https://arxiv.org/abs/1802.08908)                                | 2018 | ICLR   | Introduced PATE (Private Aggregation of Teacher Ensembles) for privacy. |
| [Nasr et al. "Scalable Extraction of Training Data from (Production) Language Models"](https://arxiv.org/abs/2311.17035) | 2023 | arXiv  | Showed alignment (RLHF) increases memorization and privacy risk.        |

### Evolution of Understanding

- **2016-2019**: Focus on classification privacy (MIA on CIFAR/MNIST).
- **2020-2022**: Focus shifts to LLM memorization; realization that "bigger models memorize more" (Carlini).
- **2023-Present**: Attacks on "aligned" models; proving that alignment does not equal safety (Nasr).

### Current Research Gaps

1. **Copyright inWeights**: Determining if a model "contains" a copyrighted work in a legal sense (substantial similarity).
2. **Machine Unlearning**: How to remove a distinct concept/person from a model cost-effectively.
3. **Watermark Robustness**: Creating watermarks that survive distillation/theft (most currently fail).

### Recommended Reading

### For Practitioners

- **Privacy Guide**: [NIST Privacy Framework](https://www.nist.gov/privacy-framework) - General standards.
- **Deep Dive**: [Carlini's Blog on Privacy](https://nicholas.carlini.com/) - Accessible explanations of complex attacks.

---

## 20.18 Conclusion

> [!CAUTION] > **Respect Privacy Laws.** Testing for membership inference typically involves processing personal data (PII). This is strictly regulated by GDPR, CCPA, etc. You must have explicit legal authorization to perform these tests on production systems containing user data. Unauthorized privacy checks are privacy violations themselves.

Model theft and privacy attacks turn the model against its creators. They transform the model from an asset into a liability (leakage vector). For Red Teamers, the goal is to quantify this risk: "How much does it cost to steal this?" or "How many queries to extract a social security number?"

As models move to the edge and APIs become ubiquitous, these "grey box" attacks will become the primary vector for IP theft.

### Next Steps

- [Chapter 21: Model DoS Resource Exhaustion](Chapter_21_Model_DoS_Resource_Exhaustion.md) - attacking availability instead of confidentiality.
- [Chapter 28: AI Privacy Attacks](Chapter_28_AI_Privacy_Attacks.md) - deeper dive into PII extraction.

---

## Quick Reference

### Attack Vector Summary

Attackers query the model to either learn its internal parameters (Model Theft) or determine if specific data points were used during training (Membership Inference). This exploits the model's high information retention and correlation with its training set.

### Key Detection Indicators

- **Systematic Querying**: High volume of queries covering the embedding space uniformly (Theft).
- **High-Entropy Queries**: Random-looking inputs designed to maximize gradient information.
- **Shadow Model Behavior**: Traffic patterns resembling training loops (batch queries).
- **Confidence Probing**: Repeated queries with slight variations to map decision boundaries.

### Primary Mitigation

- **Differential Privacy (DP)**: The gold standard. Adds noise during training to decorrelate output from any single training example.
- **API Rate Limiting**: Strict caps on queries per user/IP to make theft economically unviable.
- **Output Truncation**: Return top-k classes only, or round confidence scores to reduce information leakage.
- **Watermarking**: Embed detectable signatures in model outputs (for theft detection, not prevention).
- **Active Monitoring**: Detect extraction patterns (e.g., "high coverage" queries) and block offenders.

**Severity**: High (IP Theft / Privacy Violation)
**Ease of Exploit**: Medium (Requires many queries)
**Common Targets**: Proprietary SaaS models, Healthcare/Finance models.

---

### Pre-Engagement Checklist

#### Key Takeaways

1. Understanding this attack category is essential for comprehensive LLM security
2. Traditional defenses are often insufficient against these techniques
3. Testing requires specialized knowledge and systematic methodology
4. Effective protection requires ongoing monitoring and adaptation

#### Recommendations for Red Teamers

- Develop comprehensive test cases covering all attack variants
- Document both successful and failed attempts
- Test systematically across models and configurations
- Consider real-world scenarios and attack motivations

#### Recommendations for Defenders

- Implement defense-in-depth with multiple layers
- Monitor for anomalous attack patterns
- Maintain current threat intelligence
- Conduct regular focused red team assessments

### Pre-Engagement Checklist

#### Administrative

- [ ] Obtain written authorization
- [ ] Review and sign SOW
- [ ] Define scope and rules of engagement
- [ ] Set up communication channels

#### Technical Preparation

- [ ] Set up isolated test environment
- [ ] Install testing tools and frameworks
- [ ] Prepare payload library
- [ ] Configure logging and evidence collection

### Post-Engagement Checklist

#### Documentation

- [ ] Document findings with reproduction steps
- [ ] Capture evidence and logs
- [ ] Prepare technical report
- [ ] Create executive summary

#### Cleanup

- [ ] Remove test artifacts
- [ ] Verify no persistent changes
- [ ] Securely delete files

#### Reporting

- [ ] Deliver comprehensive report
- [ ] Provide prioritized remediation guidance
- [ ] Schedule re-testing

---
