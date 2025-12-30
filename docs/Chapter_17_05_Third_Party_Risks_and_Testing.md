## 17.7 Third-Party Integration Risks

### The Third-Party Security Challenge

When LLMs integrate with third-party services, the attack surface expands dramatically. You're not just trusting your own code anymore—you're trusting every external dependency, API, and service your plugin touches. A compromise in any one of those components can cascade right into your LLM system.

### Why Third-Party Integrations are Risky

1. **Limited Control**: You can't fix third-party code or secure their infrastructure.
2. **Supply Chain Attacks**: Compromised dependencies can introduce malware into your environment.
3. **Data Sharing**: Sensitive data leaves your perimeter and flows to external systems.
4. **Transitive Trust**: If they get compromised, you effectively get compromised too.
5. **Hidden Vulnerabilities**: You have no visibility into the security posture of your dependencies.

### Risk Categories

- Supply chain poisoning (malicious packages).
- Data leakage to third parties.
- Service compromise and pivoting.
- Dependency vulnerabilities.
- API abuse and unauthorized access.

### 17.7.1 Supply Chain Security

#### Understanding Supply Chain Risks

Supply chain attacks target the development and deployment pipeline. An attacker compromises a widely-used dependency—a library, plugin, or service—which then infects every system using it. For LLMs, this could mean malicious code hidden in popular plugin frameworks or compromised API services.

#### Attack Vectors

1. **Malicious Package**: Attacker publishes a trojanized package.
2. **Account Takeover**: Compromising a maintainer account to push a malicious update.
3. **Typosquatting**: Creating packages with names like "requsts" to catch typing errors.
4. **Dependency Confusion**: Tricking the system into using a public malicious package instead of a private internal one.

#### Dependency Scanning Example

#### Dependency scanning

```python
class DependencyScanner:
    """Scan dependencies for vulnerabilities"""

    def scan_requirements(self, requirements_file):
        """Check dependencies against vulnerability databases"""
        vulnerabilities = []

        with open(requirements_file) as f:
            for line in f:
                if '==' in line:
                    package, version = line.strip().split('==')
                    vulns = self.check_vulnerability_db(package, version)
                    vulnerabilities.extend(vulns)

        return vulnerabilities
```

### 17.7.2 Data Sharing Concerns

#### PII protection when sharing with third parties

```python
class PIIProtection:
    """Protect PII before third-party sharing"""

    def sanitize_data(self, data):
        """Remove PII before sharing"""
        pii_patterns = {
            'ssn': r'\d{3}-\d{2}-\d{4}',
            'credit_card': r'\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        }

        sanitized = data
        for pii_type, pattern in pii_patterns.items():
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)

        return sanitized
```

### 17.7.3 Service Compromise Detection

#### Monitor third-party service integrity

```python
class ServiceMonitor:
    """Monitor third-party services for compromise"""

    def verify_service(self, service_url):
        """Check service hasn't been compromised"""
        current_response = self.probe_service(service_url)
        baseline = self.get_baseline(service_url)

        if self.detect_anomalies(baseline, current_response):
            self.alert_security_team(service_url)
            return False

        return True
```

---

## 17.8 Supply Chain Attacks

### 17.8.1 Plugin Poisoning

#### Detecting malicious plugins

```python
class PluginScanner:
    """Scan plugins for malicious code"""

    def scan_plugin(self, plugin_code):
        """Static analysis for malicious patterns"""
        issues = []

        dangerous_imports = ['os.system', 'subprocess', 'eval', 'exec']
        for dangerous in dangerous_imports:
            if dangerous in plugin_code:
                issues.append(f"Dangerous import: {dangerous}")

        return issues
```

### 17.8.2 Dependency Confusion

#### Preventing dependency confusion

```python
# pip.conf - prefer private registry
[global]
index-url = https://private-pypi.company.com/simple
extra-index-url = https://pypi.org/simple

# Validate package sources
class PackageValidator:
    def validate_source(self, package_name):
        """Ensure internal packages from private registry"""
        if package_name.startswith('company-'):
            source = self.get_package_source(package_name)
            if source != 'private-pypi.company.com':
                raise SecurityError(f"Wrong source: {source}")
```

---

## 17.9 Testing Plugin Security

**Understanding Security Testing for Plugins:**

Security testing validates that plugins don't open the door to attackers before they're deployed. Traditional testing asks "does it work?", but security testing asks "can it be exploited?" For LLM plugins, this is do-or-die because they execute in trusted contexts and handle user-controlled data.

**Two Testing Approaches:**

1. **Static Analysis**: Reading the code without running it (fast, catches obvious flaws).
2. **Dynamic Testing**: Running the code with malicious inputs (slower, catches runtime issues).

You need both.

### 17.9.1 Static Analysis

**Understanding Static Analysis:**

Static analysis inspects source code to find security issues without actually executing it. Imagine a code review performed by a robot that knows every dangerous pattern in the book. For plugin security, static analysis catches:

- Dangerous function calls (`eval`, `exec`, `os.system`).
- Hardcoded secrets (API keys, passwords).
- SQL injection risks (string concatenation in queries).
- Path traversal vulnerabilities (user-controlled file paths).

**How This Analyzer Works:**

**1. AST Parsing:**

```python
tree = ast.parse(code)
```

Python's `ast` module parses code into an Abstract Syntax Tree—a structured map of your code where every function call and variable is a node.

Example:

```python
eval(user_input)
```

Becomes:

```
Call
├── func: Name(id='eval')
└── args: [Name(id='user_input')]
```

**2. Tree Walking:**

```python
for node in ast.walk(tree):
    if isinstance(node, ast.Call):  # Found a function call
```

`ast.walk(tree)` visits every node. We check if each node is a function call.

**3. Dangerous Function Detection:**

```python
if node.func.id in ['eval', 'exec']:
    issues.append({
        'severity': 'HIGH',
        'type': 'dangerous_function',
        'line': node.lineno
    })
```

If the function name is `eval` or `exec`, it flags a HIGH severity issue with the exact line number.

**Why This Catches Vulnerabilities:**

**Example 1: eval() Detection**

```python
# Plugin code
def calculate(expression):
    return eval(expression)  # Line 5
```

Static analyzer:

1. Parses code into AST.
2. Finds `Call` node for `eval`.
3. Reports: `{'severity': 'HIGH', ...}`.
4. Developer is notified BEFORE deployment.

**Example 2: Missing Detection (Limitation)**

```python
# Obfuscated dangerous call
import importlib
builtins = importlib.import_module('builtins')
builtins.eval(user_input)  # Static analysis might miss this
```

Static analysis limitations:

- Can't catch all obfuscation.
- May produce false positives.
- Doesn't validate runtime behavior.

**Extended Pattern Detection:**

Production analyzers should detect:

```python
DANGEROUS_PATTERNS = {
    'code_execution': ['eval', 'exec', 'compile', '__import__'],
    'command_injection': ['os.system', 'subprocess.Popen', 'subprocess.call'],
    'file_operations': ['open', 'file'],  # When path is user-controlled
    'deserialization': ['pickle.loads', 'yaml.unsafe_load'],
    'network': ['socket.socket', 'urllib.request.urlopen']  # Unrestricted
}
```

**Best Practice Integration:**

Run static analysis in your CI/CD pipeline:

```bash
# Pre-commit hook
#!/bin/bash
python plugin_analyzer.py plugin_code.py
if [ $? -ne 0 ]; then
    echo "Security issues found. Commit blocked."
    exit 1
fi
```

```python
import ast

class PluginAnalyzer:
    """Static analysis of plugin code"""

    def analyze(self, code):
        """Find security issues in plugin code"""
        tree = ast.parse(code)
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec']:
                        issues.append({
                            'severity': 'HIGH',
                            'type': 'dangerous_function',
                            'line': node.lineno
                        })

        return issues
```

**Real-World Tools:**

- **Bandit**: Python security linter (detects 50+ vulnerability patterns).
- **Semgrep**: Pattern-based static analysis (custom rules).
- **PyLint**: Code quality + basic security checks.
- **Safety**: Dependency vulnerability scanner.

### 17.9.2 Dynamic Testing

**Understanding Fuzzing:**

Fuzzing sends thousands of malformed or unexpected inputs to functions to try and trigger crashes, exceptions, or exploitable behaviors. Unlike static analysis, fuzzing actually **executes** the code, catching:

- Unhandled edge cases.
- Type confusion bugs.
- Buffer overflows (in C extensions).
- Logic errors that only show up at runtime.

**How This Fuzzer Works:**

**1. Input Generation:**

```python
fuzz_input = self.generate_input()
```

Generates random, malformed, or malicious inputs:

- **Random strings**: `"ãä¸­æ–‡ðŸ'©â€ðŸ'»"`
- **Extreme values**: `-999999999`, `sys.maxsize`
- **Type mismatches**: `None`, `[]`, `{}` when expecting a string
- **Injection payloads**: `"'; DROP TABLE users--"`, `"../../etc/passwd"`
- **Special characters**: Null bytes, newlines, Unicode

**2. Execution and Crash Detection:**

```python
try:
    plugin.execute(fuzz_input)
except Exception as e:
    crashes.append({'input': fuzz_input, 'error': str(e)})
```

Executes the plugin with fuzz input:

- Exception raised → Potential vulnerability.
- Unexpected behavior → Security issue.
- No error → Input handled correctly.

**3. Crash Analysis:**

```python
return crashes  # List of inputs that caused exceptions
```

**Fuzzing Example:**

**Plugin Under Test:**

```python
def process_user_input(data):
    # Vulnerable: assumes data is dict with 'name' key
    return f"Hello, {data['name']}"
```

**Fuzzer Discovers:**

```python
fuzz_input = None
plugin.execute(fuzz_input)  # TypeError: 'NoneType' object is not subscriptable

fuzz_input = "string instead of dict"
plugin.execute(fuzz_input)  # TypeError: string indices must be integers

fuzz_input = {'wrong_key': 'value'}
plugin.execute(fuzz_input)  # KeyError: 'name'
```

All three crashes indicate a lack of input validation.

**Advanced Fuzzing Strategies:**

**1. Coverage-Guided Fuzzing:**

```python
import coverage

def coverage_guided_fuzz(plugin, iterations=10000):
    cov = coverage.Coverage()
    interesting_inputs = []

    for i in range(iterations):
        fuzz_input = generate_input()
        cov.start()
        try:
            plugin.execute(fuzz_input)
        except:
            pass
        cov.stop()

        if increased_coverage(cov):
            interesting_inputs.append(fuzz_input)  # Keeps inputs that explore new code paths

    return interesting_inputs
```

**2. Mutation-Based Fuzzing:**

```python
def mutate(seed_input):
    mutations = [
        seed_input + "' OR '1'='1",  # SQL injection
        seed_input.replace('a', '../'),  # Path traversal
        seed_input * 10000,  # DoS through large input
        seed_input + "\x00",  # Null byte injection
    ]
    return random.choice(mutations)
```

**3. Grammar-Based Fuzzing:**

```python
# Generate syntactically valid but semantically malicious inputs
JSON_GRAMMAR = {
    "object": {"{}", '{"key": "' + inject_payload() + '"}'}
}
```

**Integration with CI/CD:**

```python
# pytest integration
def test_plugin_fuzzing():
    fuzzer = PluginFuzzer()
    crashes = fuzzer.fuzz(MyPlugin(), iterations=1000)

    assert len(crashes) == 0, f"Fuzzing found {len(crashes)} crashes: {crashes}"
```

```python
class PluginFuzzer:
    """Fuzz test plugin inputs"""

    def fuzz(self, plugin, iterations=1000):
        """Test plugin with random inputs"""
        crashes = []

        for i in range(iterations):
            fuzz_input = self.generate_input()
            try:
                plugin.execute(fuzz_input)
            except Exception as e:
                crashes.append({'input': fuzz_input, 'error': str(e)})

        return crashes
```

**Real-World Fuzzing Tools:**

- **Atheris**: Python coverage-guided fuzzer (Google).
- **Hypothesis**: Property-based testing (generates test cases).
- **AFL (American Fuzzy Lop)**: Binary fuzzer (for C extensions).
- **LibFuzzer**: LLVM fuzzer (integrates with Python C extensions).

**Combined Testing Strategy:**

1. **Static Analysis** (pre-commit): Catches obvious flaws instantly.
2. **Unit Tests** (CI): Validates expected behavior.
3. **Fuzzing** (nightly): Discovers edge cases over time.
4. **Penetration Testing** (pre-release): Human expertise finds logic flaws.
5. **Bug Bounty** (production): Crowdsourced security testing.

**Prerequisites:**

- Understanding of Python AST module.
- Familiarity with fuzzing concepts.
- Knowledge of common vulnerability patterns.
- CI/CD pipeline integration experience.

---

## 17.10 API Security Testing

### 17.10.1 Authentication Testing

```python
class AuthTester:
    """Test API authentication"""

    def test_brute_force_protection(self, login_endpoint):
        """Test if brute force is prevented"""
        for i in range(20):
            response = requests.post(login_endpoint, json={
                'username': 'admin',
                'password': f'wrong{i}'
            })

            if response.status_code == 429:
                return f"Rate limited after {i+1} attempts"

        return "No brute force protection"
```

### 17.10.2 Authorization Testing

```python
class AuthzTester:
    """Test authorization controls"""

    def test_idor(self, base_url, user_token):
        """Test for IDOR vulnerabilities"""
        findings = []

        for user_id in range(1, 100):
            url = f"{base_url}/api/users/{user_id}"
            response = requests.get(url, headers={
                'Authorization': f'Bearer {user_token}'
            })

            if response.status_code == 200:
                findings.append(f"Accessed user {user_id}")

        return findings
```

---
