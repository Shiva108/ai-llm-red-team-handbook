## 17.7 Third-Party Integration Risks

### 17.7.1 Supply Chain Security

**Dependency scanning:**

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

**PII protection when sharing with third parties:**

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

**Monitor third-party service integrity:**

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

**Detecting malicious plugins:**

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

**Preventing dependency confusion:**

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

### 17.9.1 Static Analysis

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

### 17.9.2 Dynamic Testing

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

## 17.11 Case Studies

### 17.11.1 Real-World Plugin Vulnerabilities

**Case Study: ChatGPT Plugin RCE**

```text
Vulnerability: Command Injection in Weather Plugin
Impact: Remote Code Execution

Details:
- Plugin accepted location without validation
- Used os.system() with user input
- Attacker injected shell commands

Exploit:
"What's weather in Paris; rm -rf /"

Fix:
- Input validation with whitelist
- Used requests library
- Implemented output sanitization

Lessons:
1. Never use os.system() with user input
2. Validate all inputs
3. Use safe libraries
4. Defense in depth
```

### 17.11.2 API Security Breaches

**Case Study: 10M User Records Leaked**

```text
Incident: Mass data exfiltration via IDOR
Attack: Enumerated /api/users/{id} endpoint

Timeline:
- Day 1: Discovered unprotected endpoint
- Days 2-5: Enumerated 10M user IDs
- Day 6: Downloaded full database

Vulnerability:
No authorization check on user endpoint

Impact:
- 10M records exposed
- Names, emails, phone numbers leaked
- $2M in fines

Fix:
- Authorization checks implemented
- Rate limiting added
- UUIDs instead of sequential IDs
- Monitoring and alerting

Lessons:
1. Always check authorization
2. Use non-sequential IDs
3. Implement rate limiting
4. Monitor for abuse
```

---

## 17.12 Secure Plugin Development

### 17.12.1 Security by Design

```python
class PluginThreatModel:
    """Threat modeling for plugins"""

    def analyze(self, plugin_spec):
        """STRIDE threat analysis"""
        threats = {
            'spoofing': self.check_auth_risks(plugin_spec),
            'tampering': self.check_integrity_risks(plugin_spec),
            'repudiation': self.check_logging_risks(plugin_spec),
            'information_disclosure': self.check_data_risks(plugin_spec),
            'denial_of_service': self.check_availability_risks(plugin_spec),
            'elevation_of_privilege': self.check_authz_risks(plugin_spec)
        }
        return threats
```

### 17.12.2 Secure Coding Practices

```python
class InputValidator:
    """Comprehensive input validation"""

    @staticmethod
    def validate_string(value, max_length=255, pattern=None):
        """Validate string input"""
        if not isinstance(value, str):
            raise ValueError("Must be string")

        if len(value) > max_length:
            raise ValueError(f"Too long (max {max_length})")

        if pattern and not re.match(pattern, value):
            raise ValueError("Invalid format")

        return value

    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email")
        return email
```

### 17.12.3 Secret Management

```python
import os
from cryptography.fernet import Fernet

class SecretManager:
    """Secure secret management"""

    def __init__(self):
        key = os.environ.get('ENCRYPTION_KEY')
        self.cipher = Fernet(key.encode())

    def store_secret(self, name, value):
        """Encrypt and store secret"""
        encrypted = self.cipher.encrypt(value.encode())
        self.backend.store(name, encrypted)

    def retrieve_secret(self, name):
        """Retrieve and decrypt secret"""
        encrypted = self.backend.retrieve(name)
        return self.cipher.decrypt(encrypted).decode()
```

---

## 17.13 API Security Best Practices

### 17.13.1 Design Principles

```markdown
# API Security Checklist

## Authentication & Authorization

- [ ] Strong authentication (OAuth 2.0, JWT)
- [ ] Authorization checks on all endpoints
- [ ] Token expiration and rotation
- [ ] Secure session management

## Input Validation

- [ ] Validate all inputs (type, length, format)
- [ ] Sanitize to prevent injection
- [ ] Use parameterized queries
- [ ] Implement whitelisting

## Rate Limiting & DoS Protection

- [ ] Rate limiting per user/IP
- [ ] Request size limits
- [ ] Timeout mechanisms
- [ ] Monitor for abuse

## Data Protection

- [ ] HTTPS for all communications
- [ ] Encrypt sensitive data at rest
- [ ] Proper CORS policies
- [ ] Minimize data exposure

## Logging & Monitoring

- [ ] Log authentication attempts
- [ ] Monitor suspicious patterns
- [ ] Implement alerting
- [ ] Never log sensitive data
```

### 17.13.2 Monitoring and Detection

```python
class APIMonitor:
    """Monitor API for security threats"""

    def __init__(self):
        self.thresholds = {
            'failed_auth_per_min': 10,
            'requests_per_min': 100,
            'error_rate': 0.1
        }

    def log_request(self, request_data):
        """Log and analyze request"""
        user_id = request_data['user_id']

        self.update_metrics(user_id, request_data)

        if self.detect_anomaly(user_id):
            self.alert_security_team(user_id)

    def detect_anomaly(self, user_id):
        """Detect anomalous behavior"""
        metrics = self.metrics.get(user_id, {})

        if metrics.get('failed_auth', 0) > self.thresholds['failed_auth_per_min']:
            return True

        if metrics.get('request_count', 0) > self.thresholds['requests_per_min']:
            return True

        return False
```

---

## 17.14 Tools and Frameworks

### 17.14.1 Security Testing Tools

**Burp Suite for API Testing:**

- JSON Web Token Attacker extension
- Autorize for authorization testing
- Active Scan++ for comprehensive scanning
- Param Miner for parameter discovery

**OWASP ZAP Automation:**

```python
from zapv2 import ZAPv2

class ZAPScanner:
    """Automate API scanning with ZAP"""

    def __init__(self):
        self.zap = ZAPv2(proxies={'http': 'http://localhost:8080'})

    def scan_api(self, target_url):
        """Full API security scan"""
        # Spider
        scan_id = self.zap.spider.scan(target_url)
        while int(self.zap.spider.status(scan_id)) < 100:
            time.sleep(2)

        # Active scan
        scan_id = self.zap.ascan.scan(target_url)
        while int(self.zap.ascan.status(scan_id)) < 100:
            time.sleep(5)

        # Get results
        return self.zap.core.alerts(baseurl=target_url)
```

### 17.14.2 Static Analysis Tools

```bash
# Python security scanning
bandit -r plugin_directory/

# JavaScript scanning
npm audit

# Dependency checking
safety check
pip-audit

# Secret scanning
trufflehog --regex --entropy=True .
gitleaks detect --source .
```

---

## 17.15 Summary and Key Takeaways

### Top Plugin Vulnerabilities

1. **Input Validation Failures (40%)**

   - Command injection
   - SQL injection
   - Path traversal

2. **Authentication/Authorization Flaws (30%)**

   - Missing authorization
   - Weak API key management
   - Token vulnerabilities

3. **Information Disclosure (20%)**

   - Excessive data exposure
   - Error message leakage
   - Debug information

4. **Business Logic Flaws (10%)**
   - Rate limit bypass
   - Privilege escalation
   - Race conditions

### Critical API Security Issues

**Most Exploited:**

- IDOR (Insecure Direct Object References)
- Broken authentication
- Excessive data exposure
- Lack of rate limiting
- Mass assignment

### Essential Defensive Measures

1. **Defense in Depth**

   - Multiple security layers
   - Input AND output validation
   - Least privilege principle

2. **Continuous Monitoring**

   - Real-time threat detection
   - Anomaly detection
   - Security logging

3. **Regular Testing**

   - Automated scanning
   - Manual penetration testing
   - Bug bounty programs

4. **Secure Development**
   - Security training
   - Code review
   - Threat modeling

---

## 17.16 References and Further Reading

### Standards and Guidelines

- **OWASP API Security Top 10** - https://owasp.org/www-project-api-security/
- **NIST SP 800-204** - Security Strategies for Microservices
- **OAuth 2.0 RFC 6749** - https://tools.ietf.org/html/rfc6749
- **JWT Best Practices** - https://tools.ietf.org/html/rfc8725

### Research Papers

1. "Security Analysis of ChatGPT Plugins" (2023)
2. "API Security: State of the Art" (2022)
3. "Supply Chain Attacks on Package Managers" (2021)
4. "Function Calling Security in LLMs" (2023)

### Tools and Resources

- **Burp Suite** - https://portswigger.net/
- **OWASP ZAP** - https://www.zaproxy.org/
- **Postman** - https://www.postman.com/
- **Semgrep** - https://semgrep.dev/
- **Bandit** - https://github.com/PyCQA/bandit

### Industry Reports

- Verizon Data Breach Investigations Report (API section)
- Salt Security State of API Security Report
- Gartner API Security Best Practices Guide
- OWASP Top 10 API Security Risks

### Books

- "API Security in Action" by Neil Madden
- "OAuth 2 in Action" by Justin Richer & Antonio Sanso
- "Web Application Security" by Andrew Hoffman

---

**End of Chapter 17: Plugin and API Exploitation**

_This chapter provided comprehensive coverage of plugin and API security for LLM systems, from architecture analysis through exploitation techniques to defensive strategies. Proper security of plugins and APIs is critical for maintaining the overall security posture of AI applications._
