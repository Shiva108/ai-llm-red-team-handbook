## 17.3 API Authentication and Authorization

### 17.3.1 Authentication Mechanisms

#### Why Authentication Matters

Authentication determines **who** can access your API. Without proper checks, anyone can invoke plugin functions, leading to unauthorized data access, service abuse, and potential security breaches. LLM plugins often handle sensitive operations—like database queries, file access, or external API calls—making robust authentication critical.

#### Common Authentication Patterns

1. **API Keys**: Simple tokens for service-to-service auth.
2. **OAuth 2.0**: Delegated authorization for user context.
3. **JWT (JSON Web Tokens)**: Self-contained auth tokens.
4. **mTLS (Mutual TLS)**: Certificate-based authentication.

#### API Key Management

API keys are the simplest authentication mechanism, but they require careful handling. The code below demonstrates how to securely generate, store, and validate them.

**Key principles:**

- Never store keys in plaintext (always hash).
- Generate cryptographically secure random keys.
- Track usage and implement rotation.
- Revoke compromised keys immediately.

```python
import secrets
import hashlib
import time

class APIKeyManager:
    """Secure API key generation and validation"""

    def generate_api_key(self, user_id):
        """Generate secure API key"""
        # Generate random key
        random_bytes = secrets.token_bytes(32)
        key = secrets.token_urlsafe(32)

        # Hash for storage (never store plaintext)
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        # Store with metadata
        self.store_key(key_hash, {
            'user_id': user_id,
            'created_at': time.time(),
            'last_used': None,
            'usage_count': 0
        })

        # Return key only once
        return key

    def validate_key(self, provided_key):
        """Validate API key"""
        key_hash = hashlib.sha256(provided_key.encode()).hexdigest()

        key_data = self.get_key(key_hash)
        if not key_data:
            return False

        # Update usage stats
        self.update_key_usage(key_hash)

        return True

# Security best practices
# 1. Never log API keys
# 2. Use HTTPS only
# 3. Implement rate limiting
# 4. Rotate keys regularly
# 5. Revoke compromised keys immediately
```

## OAuth 2.0 Implementation

**Understanding OAuth 2.0 for LLM Plugins:**

OAuth 2.0 is the industry standard for delegated authorization. It allows plugins to access user resources without ever seeing passwords. This is critical for LLM plugins interacting with external services (like Gmail, Salesforce, or GitHub) on behalf of users—you don't want to store credentials that could be compromised.

**Why OAuth 2.0 Matters:**

Traditional authentication requires users to hand over their password to every plugin. If a plugin is compromised, the attacker gets full account access. OAuth 2.0 solves this by issuing **limited-scope, revocable tokens** instead.

**OAuth 2.0 Flow Explained:**

The authorization code flow (most secure for server-side plugins) works like this:

1. **Authorization Request**: The plugin redirects any user to the OAuth provider (Google, GitHub, etc.).
2. **User Consent**: The user sees a permission screen and approves access.
3. **Authorization Code**: The provider redirects back with a temporary code.
4. **Token Exchange**: The plugin's backend exchanges the code for an access token (the client secret never hits the browser).
5. **API Access**: The plugin uses the access token for authenticated API requests.

**Why OAuth is Secure:**

- ✅ **No Password Sharing**: Users never give passwords to the plugin.
- ✅ **Scoped Permissions**: Tokens only grant specific permissions (e.g., "read email" not "delete account").
- ✅ **Token Expiration**: Access tokens expire (typically in 1 hour), limiting damage if stolen.
- ✅ **Revocation**: Users can revoke plugin access without changing their password.
- ✅ **Auditability**: OAuth providers log which apps accessed what data.

**How This Implementation Works:**

**1. Authorization URL Generation:**

```python
def get_authorization_url(self, state, scope):
    params = {
        'client_id': self.client_id,
        'redirect_uri': self.redirect_uri,
        'response_type': 'code',
        'scope': scope,
        'state': state  # CSRF protection
    }
    return f"{self.auth_endpoint}?{urlencode(params)}"
```

**Parameters explained:**

- `client_id`: Your plugin's public identifier (registered with the OAuth provider).
- `redirect_uri`: Where the provider sends the user after authorization (must be pre-registered).
- `response_type=code`: Requesting an authorization code (not a direct token, which is less secure).
- `scope`: Permissions requested (e.g., `read:user email`).
- `state`: Random value to prevent CSRF attacks (verified on callback).

**CSRF Protection via state parameter:**

```python
# Before redirect
state = secrets.token_urlsafe(32)  # Generate random state
store_in_session('oauth_state', state)
redirect_to(get_authorization_url(state, 'read:user'))

# On callback
received_state = request.args['state']
if received_state != get_from_session('oauth_state'):
    raise CSRFError("State mismatch - possible CSRF attack")
```

Without `state`, an attacker could trick a user into authorizing the attacker's app by forging the callback.

**2. Token Exchange:**

```python
def exchange_code_for_token(self, code):
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': self.redirect_uri,
        'client_id': self.client_id,
        'client_secret': self.client_secret  # ⚠️ Server-side only!
    }
    response = requests.post(self.token_endpoint, data=data)
    return response.json()
```

**Why this happens server-side:**

The authorization code is useless without the **client_secret**. The secret is stored securely on the plugin's backend server, never sent to the browser. This prevents:

- Malicious JavaScript from stealing the secret.
- Browser extensions from intercepting tokens.
- XSS attacks from compromising authentication.

**3. Token Response:**

```python
if response.status_code == 200:
    token_data = response.json()
    return {
        'access_token': token_data['access_token'],      # Short-lived (1 hour)
        'refresh_token': token_data.get('refresh_token'), # Long-lived (for renewal)
        'expires_in': token_data['expires_in'],          # Seconds until expiration
        'scope': token_data.get('scope')                 # Granted permissions
    }
```

**Token types:**

- **Access Token**: Used for API requests; expires quickly.
- **Refresh Token**: Used to get new access tokens without re-authenticating the user.

**4. Token Refresh:**

```python
def refresh_access_token(self, refresh_token):
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': self.client_id,
        'client_secret': self.client_secret
    }
    response = requests.post(self.token_endpoint, data=data)
    return response.json()
```

When the access token expires, use the refresh token to get a new one. This is transparent to the user—no re-authorization needed.

**Security Best Practices:**

1. **Store client_secret securely**:
   - Environment variables (not hardcoded).
   - Secret management systems (AWS Secrets Manager, HashiCorp Vault).
   - Never commit to Git.
2. **Validate redirect_uri**:

   ```python
   ALLOWED_REDIRECT_URIS = ['https://myapp.com/oauth/callback']
   if redirect_uri not in ALLOWED_REDIRECT_URIS:
       raise SecurityError("Invalid redirect URI")
   ```

   This blocks open redirect attacks where an attacker tricks the system into sending the authorization code to their server.

3. **Use PKCE for additional security** (Proof Key for Code Exchange):

   ```python
   # Generate code verifier and challenge
   code_verifier = secrets.token_urlsafe(64)
   code_challenge = base64.urlsafe_b64encode(
       hashlib.sha256(code_verifier.encode()).digest()
   ).decode().rstrip('=')

   # Send challenge in authorization request
   params['code_challenge'] = code_challenge
   params['code_challenge_method'] = 'S256'

   # Send verifier in token exchange
   data['code_verifier'] = code_verifier
   ```

   PKCE stops attackers from intercepting the authorization code.

4. **Minimal scope principle**:

   ```python
   # ❌ Bad: Request all permissions
   scope = "read write admin delete"

   # ✅ Good: Request only what's needed
   scope = "read:user"  # Just read user profile
   ```

5. **Token storage**:
   - **Access tokens**: Store in secure HTTP-only cookies or encrypted session storage.
   - **Refresh tokens**: Keep in a database with encryption at rest.
   - **Never** store in `localStorage` (it's vulnerable to XSS).

### Common Vulnerabilities

#### 1. Authorization Code Interception

- **Attack**: Attacker intercepts authorization code from redirect.
- **Defense**: PKCE ensures that even with the code, the attacker can't exchange it for a token.

#### 2. CSRF on Callback

- **Attack**: Attacker tricks victim into authorizing attacker's app.
- **Defense**: Validate `state` parameter matches original request.

#### 3. Open Redirect

- **Attack**: Attacker manipulates `redirect_uri` to steal authorization code.
- **Defense**: Strictly whitelist allowed redirect URIs.

#### 4. Token Leakage

- **Attack**: Access token exposed in logs, URLs, or client-side storage.
- **Defense**: Never log tokens, never put them in URLs, and always use HTTP-only cookies.

### Real-World Example

```python
# Plugin requests Gmail access
oauth = OAuth2Plugin(
    client_id="abc123.apps.googleusercontent.com",
    client_secret=os.environ['GOOGLE_CLIENT_SECRET'],
    redirect_uri="https://myplugin.com/oauth/callback"
)

# Step 1: Redirect user to Google
state = secrets.token_urlsafe(32)
auth_url = oauth.get_authorization_url(
    state=state,
    scope="https://www.googleapis.com/auth/gmail.readonly"
)
return redirect(auth_url)

# Step 2: Handle callback
@app.route('/oauth/callback')
def oauth_callback():
    code = request.args['code']
    state = request.args['state']

    # Verify state (CSRF protection)
    if state != session['oauth_state']:
        abort(403)

    # Exchange code for token
    tokens = oauth.exchange_code_for_token(code)

    # Store tokens securely
    session['access_token'] = tokens['access_token']
    session['refresh_token'] = encrypt(tokens['refresh_token'])

    return "Authorization successful!"

# Step 3: Use token for API requests
@app.route('/read-emails')
def read_emails():
    access_token = session['access_token']

    response = requests.get(
        'https://gmail.googleapis.com/gmail/v1/users/me/messages',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    return response.json()
```

**Prerequisites:**

- Understanding of HTTP redirects and callbacks.
- Knowledge of OAuth 2.0 roles (client, resource owner, authorization server).
- Familiarity with token-based authentication.
- Awareness of common web security vulnerabilities (CSRF, XSS).

**Implementation Example:**

```python
class OAuth2Plugin:
    """Secure OAuth 2.0 flow for plugin authentication"""

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_endpoint = "https://oauth.example.com/token"
        self.auth_endpoint = "https://oauth.example.com/authorize"

    def get_authorization_url(self, state, scope):
        """Generate authorization URL"""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'state': state  # CSRF protection
        }
        return f"{self.auth_endpoint}?{urlencode(params)}"

    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        response = requests.post(self.token_endpoint, data=data)

        if response.status_code == 200:
            token_data = response.json()
            return {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'expires_in': token_data['expires_in'],
                'scope': token_data.get('scope')
            }
        else:
            raise OAuthError("Token exchange failed")

    def refresh_access_token(self, refresh_token):
        """Refresh expired access token"""
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }

        response = requests.post(self.token_endpoint, data=data)
        return response.json()
```

**Testing OAuth Implementation:**

```python
def test_oauth_flow():
    # Test authorization URL generation
    oauth = OAuth2Plugin('client_id', 'secret', 'https://app.com/callback')
    auth_url = oauth.get_authorization_url('state123', 'read:user')

    assert 'client_id=client_id' in auth_url
    assert 'state=state123' in auth_url
    assert 'response_type=code' in auth_url

    # Test token exchange (with mocked OAuth provider)
    with mock_oauth_server():
        tokens = oauth.exchange_code_for_token('auth_code_123')
        assert 'access_token' in tokens
        assert 'refresh_token' in tokens
```

## JWT token security

### Understanding JWT for LLM Plugins

JSON Web Tokens (JWT) are self-contained tokens that carry authentication and authorization information. Unlike session IDs that require database lookups, JWTs are stateless—all necessary data is encoded in the token itself. This makes them ideal for distributed LLM plugin systems where centralized session storage would be a bottleneck.

### JWT Structure

A JWT consists of three parts separated by dots:

```text
header.payload.signature
```

Example:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjMsInBlcm1pc3Npb25zIjpbInJlYWQiXX0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Decoded:**

1. **Header** (Base64-encoded JSON):

   ```json
   { "alg": "HS256", "typ": "JWT" }
   ```

   - `alg`: Signing algorithm (HMAC SHA256).
   - `typ`: Token type.

2. **Payload** (Base64-encoded JSON):

   ```json
   {
     "user_id": 123,
     "permissions": ["read"],
     "iat": 1640000000,
     "exp": 1640086400,
     "jti": "unique-token-id"
   }
   ```

   - `user_id`: User identifier.
   - `permissions`: Authorization claims.
   - `iat`: Issued at (Unix timestamp).
   - `exp`: Expiration (Unix timestamp).
   - `jti`: JWT ID (for revocation).

3. **Signature** (Cryptographic hash):
   ```
   HMACSHA256(
     base64UrlEncode(header) + "." + base64UrlEncode(payload),
     secret_key
   )
   ```

### Why We Use JWTs

✅ **Stateless**: No database lookup required for validation.
✅ **Scalable**: Can be validated by any server with the secret key.
✅ **Self-Contained**: All user info is embedded in the token.
✅ **Cross-Domain**: Works across different services/plugins.
✅ **Standard**: RFC 7519, widely supported.

### Breaking Down the Code

**1. Token Creation:**

```python
def create_token(self, user_id, permissions, expiration_hours=24):
    payload = {
        'user_id': user_id,
        'permissions': permissions,
        'iat': time.time(),  # When token was issued
        'exp': time.time() + (expiration_hours * 3600),  # When it expires
        'jti': secrets.token_urlsafe(16)  # Unique token ID
    }
    token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    return token
```

**Key claims explained:**

- **iat (Issued At)**: Prevents token replay attacks from the past.
- **exp (Expiration)**: Limits token lifetime (typically 1-24 hours).
- **jti (JWT ID)**: Unique identifier for token revocation (stored in blacklist).

**2. Token Validation:**

```python
def validate_token(self, token):
    try:
        payload = jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm]  # CRITICAL: Specify allowed algorithms
        )
```

**Why `algorithms=[self.algorithm]` is critical:**

Without this, an attacker can change `alg` in the header to `none` or `HS256` when the server expects `RS256`, bypassing signature verification entirely. This is called the **algorithm confusion attack**.

**Algorithm Confusion Attack Example:**

```python
# Vulnerable code (no algorithm specification)
payload = jwt.decode(token, secret_key)  # ❌ DANGEROUS

# Attacker creates token with alg=none:
malicious_token = base64_encode('{"alg":"none"}') + '.' + base64_encode('{"user_id":1,"permissions":["admin"]}') + '.'

# Server accepts it because no algorithm was enforced!
# Result: Attacker has admin access without valid signature
```

**Secure version:**

```python
payload = jwt.decode(token, secret_key, algorithms=['HS256'])  # ✅ SAFE
# If token uses different algorithm → InvalidTokenError
```

**3. Expiration Check:**

```python
if payload['exp'] < time.time():
    raise TokenExpiredError()
```

Even if the signature is valid, you must reject expired tokens. This limits the damage if a token is stolen—it only works until expiration.

**4. Revocation Check:**

```python
if self.is_token_revoked(payload['jti']):
    raise TokenRevokedError()
```

JWTs are stateless, but you can maintain a blacklist of revoked `jti` values (in Redis or a database). This allows manual token revocation when:

- A user logs out.
- An account is compromised.
- Permissions change.

### Common JWT Vulnerabilities

#### 1. Algorithm Confusion (alg=none)

- **Attack**: Change `alg` to `none`, remove signature.
- **Defense**: Always specify `algorithms` parameter in decode.

#### 2. Weak Secret Keys

```python
# ❌ Bad: Easily brute-forced
secret_key = "secret123"

# ✅ Good: Strong random key
secret_key = secrets.token_urlsafe(64)
```

#### 3. No Expiration

```python
# ❌ Bad: Token never expires
payload = {'user_id': 123}  # Missing 'exp'

# ✅ Good: Short expiration
payload = {'user_id': 123, 'exp': time.time() + 3600}  # 1 hour
```

#### 4. Storing Sensitive Data

```python
# ❌ Bad: JWT payloads are Base64-encoded, NOT encrypted
payload = {'user_id': 123, 'password': 'secret123'}  # Visible to anyone!

# ✅ Good: Only non-sensitive data
payload = {'user_id': 123, 'permissions': ['read']}
```

#### 5. Not Validating Claims

```python
# ❌ Bad: Accept any valid JWT
payload = jwt.decode(token, secret_key, algorithms=['HS256'])

# ✅ Good: Validate issuer, audience
payload = jwt.decode(
    token,
    secret_key,
    algorithms=['HS256'],
    issuer='myapp.com',      # Only accept tokens from our app
    audience='api.myapp.com'  # Only for our API
)
```

**Security Best Practices:**

1. **Use strong cryptographic secrets**:

   ```python
   import secrets
   SECRET_KEY = secrets.token_urlsafe(64)  # 512 bits of entropy
   ```

2. **Short expiration times**:

   ```python
   'exp': time.time() + 900  # 15 minutes for access tokens
   ```

   Use refresh tokens for longer sessions.

3. **Rotate secrets regularly**:

   ```python
   # Support multiple keys for rotation
   KEYS = {
       'key1': 'old-secret',
       'key2': 'current-secret'
   }

   # Try all keys when validating
   for key_id, key in KEYS.items():
       try:
           return jwt.decode(token, key, algorithms=['HS256'])
       except jwt.InvalidTokenError:
           continue
   ```

4. **Include audience and issuer**:

   ```python
   payload = {
       'iss': 'myapp.com',          # Issuer
       'aud': 'api.myapp.com',      # Audience
       'sub': 'user123',            # Subject (user ID)
       'exp': time.time() + 3600
   }
   ```

5. **Use RS256 for public/private key scenarios**:

   ```python
   # When multiple services need to validate tokens
   # but shouldn't be able to create them

   # Token creation (private key)
   token = jwt.encode(payload, private_key, algorithm='RS256')

   # Token validation (public key)
   payload = jwt.decode(token, public_key, algorithms=['RS256'])
   ```

**HS256 vs RS256:**

| Feature     | HS256 (HMAC)              | RS256 (RSA)                        |
| :---------- | :------------------------ | :--------------------------------- |
| Key Type    | Shared secret             | Public/Private keypair             |
| Use Case    | Single service            | Multiple services                  |
| Signing     | Same key signs & verifies | Private key signs, public verifies |
| Security    | Secret must be protected  | Private key must be protected      |
| Performance | Faster                    | Slower (asymmetric crypto)         |

**When to use RS256:**

- Multiple plugins need to validate tokens.
- You don't want to share the secret with all plugins.
- Public key distribution is acceptable.

**Token Storage:**

```python
# ✅ Good: HTTP-only cookie (not accessible via JavaScript)
response.set_cookie(
    'jwt_token',
    token,
    httponly=True,  # Prevents XSS attacks
    secure=True,    # HTTPS only
    samesite='Strict'  # CSRF protection
)

# ❌ Bad: localStorage (vulnerable to XSS)
localStorage.setItem('jwt_token', token)  # JavaScript can access!
```

**Prerequisites:**

- Understanding of cryptographic signatures.
- Familiarity with Base64 encoding.
- Knowledge of token-based authentication.
- Awareness of common JWT vulnerabilities.

```python
import jwt
import time

class JWTTokenManager:
    """Secure JWT token handling"""

    def __init__(self, secret_key, algorithm='HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.revocation_list = set() # Initialize revocation list

    def create_token(self, user_id, permissions, expiration_hours=24):
        """Create JWT token"""
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'iat': time.time(),  # issued at
            'exp': time.time() + (expiration_hours * 3600),  # expiration
            'jti': secrets.token_urlsafe(16)  # JWT ID for revocation
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def validate_token(self, token):
        """Validate and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # Check expiration
            if payload['exp'] < time.time():
                raise TokenExpiredError()

            # Verify not revoked
            if self.is_token_revoked(payload['jti']):
                raise TokenRevokedError()

            return payload
        except jwt.InvalidTokenError:
            raise InvalidTokenError()

    def is_token_revoked(self, jti):
        """Check if a token is in the revocation list"""
        return jti in self.revocation_list

    def revoke_token(self, jti):
        """Revoke specific token"""
        self.revocation_list.add(jti)

# Security considerations
# 1. Use strong secret keys (256+ bits)
# 2. Short expiration times
# 3. Implement token refresh
# 4. Maintain revocation list
# 5. Use asymmetric algorithms (RS256) for better security
```

### 17.3.2 Authorization Models

#### Role-Based Access Control (RBAC)

**Understanding RBAC for LLM Plugins:**

Role-Based Access Control (RBAC) is a critical security pattern for plugin systems where different users should have different levels of access. Without it, any user could invoke any function—including administrative or destructive operations.

**Why RBAC is Critical for LLM Systems:**

LLM plugins execute functions based on prompts. If an attacker can craft a prompt that tricks the LLM into calling an admin function, the only protection is RBAC. The system must verify that the **user** (not the LLM) has actual permission to execute the requested function.

**How This Implementation Works:**

**1. Role Definition:**

```python
self.roles = {
    'admin': {'permissions': ['read', 'write', 'delete', 'admin']},
    'user': {'permissions': ['read', 'write']},
    'guest': {'permissions': ['read']}
}
```

- **admin**: Full access (all operations).
- **user**: Can read and modify their own data.
- **guest**: Read-only access.

**2. Role Hierarchy:**

```python
self.role_hierarchy = {
    'guest': 0,
    'user': 1,
    'admin': 2,
    'super_admin': 3
}
```

Numerical hierarchy allows simple comparison:

- Higher number = More privileges.
- `user_level >= required_level` check grants or denies access.

**3. Permission Checking (`has_permission`):**

```python
def has_permission(self, user_id, required_permission):
    role = self.user_roles.get(user_id)
    if not role:
        return False  # User has no role = no permissions

    permissions = self.roles[role]['permissions']
    return required_permission in permissions
```

Process:

1. Look up user's role: `user123` → `'user'`
2. Get role's permissions: `'user'` → `['read', 'write']`
3. Check if required permission exists: `'write' in ['read', 'write']` → `True`

**4. Decorator Pattern (`require_permission`):**

The decorator provides elegant function-level access control:

```python
@rbac.require_permission('write')
def modify_data(user_id, data):
    return update_database(data)
```

How it works:

1. User calls `modify_data('user123', {...})`.
2. Decorator intercepts the call.
3. Checks: Does `user123` have `'write'` permission?
4. If Yes: Function executes normally.
5. If No: Raises `PermissionDeniedError` before the function runs.

**Attack Scenarios Prevented:**

**Scenario 1: Privilege Escalation via Prompt Injection**

```text
Attacker (guest role): "Delete all user accounts"
LLM generates: modify_data('guest123', {'action': 'delete_all'})
RBAC check: guest has ['read'] permissions
Required: 'write' permission
Result: PermissionDeniedError - Attack blocked
```

**Scenario 2: Cross-User Data Access**

```text
User A: "Show me user B's private data"
LLM generates: read_private_data('userA', 'userB')
RBAC check: userA has 'read' permission (passes)
But: Function should also check ownership (separate from RBAC)
Result: RBAC allows, but ownership check should block
```

**Don't Confuse RBAC with Ownership:**

RBAC answers: "Can this **role** perform this **action type**?"

- Can a guest read? No.
- Can a user write? Yes.
- Can an admin delete? Yes.

Ownership answers: "Can this **specific user** access this **specific resource**?"

- Can userA read userB's messages? No (even though both are 'user' role).
- Can userA read their own messages? Yes.

**Both are required** for complete security:

```python
@rbac.require_permission('write')  # RBAC check
def modify_document(user_id, doc_id, changes):
    doc = get_document(doc_id)
    if doc.owner_id != user_id:  # Ownership check
        raise PermissionDeniedError()
    # Both checks passed, proceed
    doc.update(changes)
```

**Best Practices:**

1. **Least Privilege**: Assign the minimum necessary role.
2. **Explicit Denials**: No role = no permissions (fail closed).
3. **Audit Logging**: Log all permission checks and failures.
4. **Regular Review**: Audit user roles periodically.
5. **Dynamic Roles**: Allow role changes without code deployment.

**Real-World Enhancements:**

Production systems should add:

- **Attribute-Based Access Control (ABAC)**: Permissions based on user attributes (department, location, time of day).
- **Temporary Privilege Elevation**: "sudo" for admin tasks with MFA.
- **Role Expiration**: Time-limited admin access.
- **Group-Based Roles**: Users inherit permissions from groups.
- **Fine-Grained Permissions**: Instead of just 'write', use keys like 'user:update', 'user:delete', 'config:modify'.

**Testing RBAC:**

```python
# Test 1: Guest cannot write
rbac.assign_role('guest_user', 'guest')
assert rbac.has_permission('guest_user', 'write') == False

# Test 2: User can write
rbac.assign_role('normal_user', 'user')
assert rbac.has_permission('normal_user', 'write') == True

# Test 3: Admin can do everything
rbac.assign_role('admin_user', 'admin')
assert rbac.has_permission('admin_user', 'admin') == True

# Test 4: Decorator blocks unauthorized access
try:
    # As guest, try to call write function
    modify_data('guest_user', {...})
    assert False, "Should have raised PermissionDeniedError"
except PermissionDeniedError:
    pass  # Expected behavior
```

**Prerequisites:**

- Understanding of role-based access control concepts.
- Knowledge of Python decorators.
- Awareness of the difference between authentication and authorization.

```python
class RBACSystem:
    """Implement role-based access control"""

    def __init__(self):
        self.roles = {
            'admin': {
                'permissions': ['read', 'write', 'delete', 'admin']
            },
            'user': {
                'permissions': ['read', 'write']
            },
            'guest': {
                'permissions': ['read']
            }
        }
        self.user_roles = {}

    def assign_role(self, user_id, role):
        """Assign role to user"""
        if role not in self.roles:
            raise InvalidRoleError()
        self.user_roles[user_id] = role

    def has_permission(self, user_id, required_permission):
        """Check if user has required permission"""
        role = self.user_roles.get(user_id)
        if not role:
            return False

        permissions = self.roles[role]['permissions']
        return required_permission in permissions

    def require_permission(self, permission):
        """Decorator for permission checking"""
        def decorator(func):
            def wrapper(user_id, *args, **kwargs):
                if not self.has_permission(user_id, permission):
                    raise PermissionDeniedError(
                        f"User lacks permission: {permission}"
                    )
                return func(user_id, *args, **kwargs)
            return wrapper
        return decorator

# Usage
rbac = RBACSystem()
rbac.assign_role('user123', 'user')

@rbac.require_permission('write')
def modify_data(user_id, data):
    # Only users with 'write' permission can execute
    return update_database(data)
```

**Common Pitfalls:**

- **Forgetting to check permissions**: Not using `@require_permission` on sensitive functions.
- **Hardcoded roles**: Roles in code instead of database/config.
- **Confusing RBAC with ownership**: RBAC checks role, not resource ownership.
- **No audit trail**: Not logging permission denials for security monitoring.
- **Over-privileged default roles**: Giving users 'admin' by default.

### 17.3.3 Session Management
#### Secure session handling

```python
import redis
import secrets
import time

class SessionManager:
    """Secure session management for API authentication"""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.session_timeout = 3600  # 1 hour

    def create_session(self, user_id, metadata=None):
        """Create new session"""
        session_id = secrets.token_urlsafe(32)

        session_data = {
            'user_id': user_id,
            'created_at': time.time(),
            'last_activity': time.time(),
            'metadata': metadata or {}
        }

        # Store in Redis with expiration
        self.redis.setex(
            f"session:{session_id}",
            self.session_timeout,
            json.dumps(session_data)
        )

        return session_id

    def validate_session(self, session_id):
        """Validate session and return user data"""
        session_key = f"session:{session_id}"
        session_data = self.redis.get(session_key)

        if not session_data:
            raise InvalidSessionError()

        data = json.loads(session_data)

        # Update last activity
        data['last_activity'] = time.time()
        self.redis.setex(session_key, self.session_timeout, json.dumps(data))

        return data

    def destroy_session(self, session_id):
        """Destroy session (logout)"""
        self.redis.delete(f"session:{session_id}")

    def destroy_all_user_sessions(self, user_id):
        """Destroy all sessions for a user"""
        # Iterate through all sessions and delete matching user_id
        for key in self.redis.scan_iter("session:*"):
            session_data = json.loads(self.redis.get(key))
            if session_data['user_id'] == user_id:
                self.redis.delete(key)
```

### 17.3.4 Common Authentication Vulnerabilities

#### API key leakage prevention

```python
import re

class SecretScanner:
    """Scan for accidentally exposed secrets"""

    def __init__(self):
        self.patterns = {
            'api_key': r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9-_]{20,})',
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'private_key': r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',
            'jwt': r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'
        }

    def scan_code(self, code):
        """Scan code for exposed secrets"""
        findings = []

        for secret_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                findings.append({
                    'type': secret_type,
                    'location': match.span(),
                    'value': match.group(0)[:20] + '...'  # Truncate
                })

        return findings

# Best practices to prevent key leakage
# 1. Use environment variables
# 2. Never commit secrets to git
# 3. Use .gitignore for config files
# 4. Implement pre-commit hooks
# 5. Use secret management services (AWS Secrets Manager, HashiCorp Vault)
```

---

