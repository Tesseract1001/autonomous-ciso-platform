"""
Professional Multi-Language Vulnerability Scanner
Supports: Python, JavaScript, TypeScript, Java, Go, PHP, Ruby, Shell, Config files
Integrates: Bandit (Python), custom regex patterns, OWASP Top 10 mapping
"""
import subprocess
import json
import re
import os
import tempfile
import zipfile
import shutil
from pathlib import Path


# ========================================================================
# OWASP TOP 10 (2021) CATEGORY MAPPING
# ========================================================================
OWASP_CATEGORIES = {
    "A01": "Broken Access Control",
    "A02": "Cryptographic Failures",
    "A03": "Injection",
    "A04": "Insecure Design",
    "A05": "Security Misconfiguration",
    "A06": "Vulnerable & Outdated Components",
    "A07": "Identification & Authentication Failures",
    "A08": "Software & Data Integrity Failures",
    "A09": "Security Logging & Monitoring Failures",
    "A10": "Server-Side Request Forgery (SSRF)",
}

# ========================================================================
# VULNERABILITY PATTERNS — Multi-Language
# ========================================================================
VULN_PATTERNS = [
    # --- Credentials & Secrets ---
    {"id": "SECRET-001", "severity": "CRITICAL", "owasp": "A02", "cwe": 798,
     "pattern": r'(?i)(password|passwd|pwd|pass)\s*[=:]\s*["\'][^"\']{4,}["\']',
     "title": "Hardcoded Password",
     "description": "A password is hardcoded in the source code. If this code is committed to a public repository, attackers gain immediate access.",
     "fix": "Move the password to an environment variable or a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault)."},

    {"id": "SECRET-002", "severity": "CRITICAL", "owasp": "A02", "cwe": 798,
     "pattern": r'(?i)(api[_-]?key|apikey|secret[_-]?key|auth[_-]?token|access[_-]?token)\s*[=:]\s*["\'][A-Za-z0-9_\-]{12,}["\']',
     "title": "Hardcoded API Key / Secret Token",
     "description": "An API key or authentication token is embedded directly in code. This allows any reader of the source to impersonate the application.",
     "fix": "Use environment variables: `os.environ.get('API_KEY')` or a `.env` file excluded from version control."},

    {"id": "SECRET-003", "severity": "CRITICAL", "owasp": "A02", "cwe": 798,
     "pattern": r'AKIA[0-9A-Z]{16}',
     "title": "AWS Access Key ID Detected",
     "description": "An AWS Access Key was found. This can be used to access AWS services, potentially leading to full cloud infrastructure compromise.",
     "fix": "Rotate the key immediately in the AWS IAM console. Use IAM roles instead of hardcoded keys."},

    {"id": "SECRET-004", "severity": "CRITICAL", "owasp": "A02", "cwe": 321,
     "pattern": r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----',
     "title": "Private Key Embedded in Source",
     "description": "A private cryptographic key is stored in the source code. This compromises all encryption that depends on this key.",
     "fix": "Remove the key from source code immediately. Store it in a secure key vault and regenerate a new key pair."},

    {"id": "SECRET-005", "severity": "HIGH", "owasp": "A02", "cwe": 798,
     "pattern": r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
     "title": "Hardcoded JWT Token",
     "description": "A JSON Web Token is embedded in the code. If this is a valid token, an attacker can use it to authenticate as the token's subject.",
     "fix": "Remove the token and generate tokens dynamically at runtime. Never store tokens in source code."},

    # --- Injection ---
    {"id": "INJ-001", "severity": "CRITICAL", "owasp": "A03", "cwe": 89,
     "pattern": r'(?i)(execute|cursor\.execute|\.query|\.raw)\s*\(\s*[f"\'].*(\{|%s|%d|\$\{|\+\s*\w)',
     "title": "SQL Injection via String Formatting",
     "description": "User input is concatenated directly into an SQL query. An attacker can inject malicious SQL to read, modify, or delete the entire database.",
     "fix": "Use parameterized queries: `cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))`"},

    {"id": "INJ-002", "severity": "CRITICAL", "owasp": "A03", "cwe": 78,
     "pattern": r'(?i)(subprocess\.(call|run|Popen|check_output)|os\.system|os\.popen)\s*\(.*shell\s*=\s*True',
     "title": "OS Command Injection",
     "description": "A shell command is constructed with user-controllable input and `shell=True`. An attacker can inject arbitrary system commands.",
     "fix": "Use `subprocess.run()` with a list of arguments and `shell=False`. Validate and sanitize all inputs."},

    {"id": "INJ-003", "severity": "HIGH", "owasp": "A03", "cwe": 79,
     "pattern": r'(?i)(innerHTML|outerHTML|document\.write|\.html\()\s*[=\(].*(\+|\$\{|`)',
     "title": "Cross-Site Scripting (XSS)",
     "description": "Untrusted data is inserted into the DOM without sanitization, allowing attackers to inject malicious scripts that steal cookies or credentials.",
     "fix": "Use `textContent` instead of `innerHTML`. Always sanitize user input with a library like DOMPurify."},

    {"id": "INJ-004", "severity": "HIGH", "owasp": "A03", "cwe": 94,
     "pattern": r'\beval\s*\(',
     "title": "Use of eval() — Code Injection Risk",
     "description": "The `eval()` function executes arbitrary code. If user input reaches eval(), an attacker achieves full code execution on the server.",
     "fix": "Replace eval() with safer alternatives. For JSON parsing, use `JSON.parse()` or `json.loads()`."},

    {"id": "INJ-005", "severity": "HIGH", "owasp": "A03", "cwe": 94,
     "pattern": r'\bexec\s*\(',
     "title": "Use of exec() — Arbitrary Code Execution",
     "description": "The `exec()` function runs arbitrary code strings. This is extremely dangerous if any user input can influence the executed code.",
     "fix": "Remove exec() calls entirely. Use function dispatching or safe interpreters instead."},

    # --- Cryptographic Failures ---
    {"id": "CRYPTO-001", "severity": "HIGH", "owasp": "A02", "cwe": 327,
     "pattern": r'(?i)(hashlib\.md5|MD5\(|md5\(|MessageDigest\.getInstance\(\s*["\']MD5)',
     "title": "Weak Hashing Algorithm (MD5)",
     "description": "MD5 is cryptographically broken. Attackers can generate collisions and reverse hashes using rainbow tables in seconds.",
     "fix": "Use bcrypt, scrypt, or Argon2 for passwords. Use SHA-256 or SHA-3 for general hashing."},

    {"id": "CRYPTO-002", "severity": "HIGH", "owasp": "A02", "cwe": 327,
     "pattern": r'(?i)(hashlib\.sha1|SHA1\(|sha1\(|MessageDigest\.getInstance\(\s*["\']SHA-?1)',
     "title": "Weak Hashing Algorithm (SHA-1)",
     "description": "SHA-1 has known collision attacks. It should not be used for security-sensitive operations like digital signatures or password hashing.",
     "fix": "Upgrade to SHA-256 or use bcrypt/Argon2 for password hashing."},

    {"id": "CRYPTO-003", "severity": "MEDIUM", "owasp": "A02", "cwe": 326,
     "pattern": r'(?i)(DES|RC4|RC2|Blowfish|ECB)',
     "title": "Weak or Obsolete Encryption Algorithm",
     "description": "A weak/obsolete encryption algorithm is in use. These can be broken with modern computing power.",
     "fix": "Use AES-256-GCM or ChaCha20-Poly1305 for encryption."},

    # --- Insecure Deserialization ---
    {"id": "DESER-001", "severity": "CRITICAL", "owasp": "A08", "cwe": 502,
     "pattern": r'pickle\.(loads|load|Unpickler)',
     "title": "Insecure Deserialization (Pickle)",
     "description": "Python's pickle module can execute arbitrary code during deserialization. An attacker can craft a malicious pickle payload to achieve remote code execution.",
     "fix": "Never unpickle data from untrusted sources. Use JSON or MessagePack for data serialization."},

    {"id": "DESER-002", "severity": "HIGH", "owasp": "A08", "cwe": 502,
     "pattern": r'(?i)(yaml\.load\s*\((?!.*Loader\s*=\s*yaml\.SafeLoader)|yaml\.unsafe_load)',
     "title": "Insecure YAML Deserialization",
     "description": "Using yaml.load() without SafeLoader allows arbitrary Python object instantiation, leading to remote code execution.",
     "fix": "Use `yaml.safe_load()` or explicitly specify `Loader=yaml.SafeLoader`."},

    # --- Access Control ---
    {"id": "ACCESS-001", "severity": "HIGH", "owasp": "A01", "cwe": 798,
     "pattern": r'(?i)(DEBUG\s*=\s*True|app\.debug\s*=\s*True|\.env.*DEBUG.*true)',
     "title": "Debug Mode Enabled in Production",
     "description": "Debug mode exposes stack traces, internal paths, and configuration to attackers. This information helps them craft targeted exploits.",
     "fix": "Set DEBUG=False in production. Use environment-specific configuration files."},

    {"id": "ACCESS-002", "severity": "MEDIUM", "owasp": "A01", "cwe": 284,
     "pattern": r'(?i)(CORS.*\*|Access-Control-Allow-Origin.*\*|allow_origins\s*=\s*\[?\s*["\']?\*)',
     "title": "Overly Permissive CORS Policy",
     "description": "Allowing all origins ('*') in CORS means any website can make requests to your API, potentially stealing sensitive data.",
     "fix": "Restrict CORS to specific trusted domains: `allow_origins=['https://yourdomain.com']`."},

    # --- Server-Side Request Forgery ---
    {"id": "SSRF-001", "severity": "HIGH", "owasp": "A10", "cwe": 918,
     "pattern": r'(?i)(requests\.get|requests\.post|urllib\.request\.urlopen|fetch|http\.get)\s*\(.*(\+|f["\']|\$\{|\%)',
     "title": "Potential Server-Side Request Forgery (SSRF)",
     "description": "User-controlled input is used to construct a URL for a server-side HTTP request. An attacker can force the server to access internal resources.",
     "fix": "Validate and whitelist allowed URLs. Block requests to internal IP ranges (e.g., 10.x.x.x, 127.0.0.1)."},

    # --- Logging & Monitoring ---
    {"id": "LOG-001", "severity": "MEDIUM", "owasp": "A09", "cwe": 532,
     "pattern": r'(?i)(print|console\.log|logger\.\w+)\s*\(.*(?:password|token|secret|key|credential|ssn|credit.?card)',
     "title": "Sensitive Data in Log Output",
     "description": "Sensitive information (passwords, tokens, etc.) is being written to logs. Logs are often stored without encryption and accessible to many people.",
     "fix": "Never log sensitive data. Use redaction or masking: `logger.info('User login: %s', mask(email))`"},

    # --- Misconfiguration ---
    {"id": "MISC-001", "severity": "MEDIUM", "owasp": "A05", "cwe": 209,
     "pattern": r'(?i)(traceback\.print_exc|raise.*Exception\(.*\+|catch.*print.*e\.message)',
     "title": "Verbose Error Messages Exposing Internals",
     "description": "Detailed error messages or stack traces are exposed to end users, leaking internal implementation details.",
     "fix": "Return generic error messages to users. Log detailed errors server-side only."},
]


def run_bandit_scan(target_dir: str) -> list[dict]:
    """Run Bandit static analysis on Python files in the target directory."""
    results = []
    try:
        cmd = [
            "bandit", "-r", target_dir,
            "-f", "json",
            "--severity-level", "low",
            "--confidence-level", "low"
        ]
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if process.stdout:
            bandit_output = json.loads(process.stdout)
            for issue in bandit_output.get("results", []):
                severity = issue.get("issue_severity", "MEDIUM").upper()
                test_id = issue.get("test_id", "unknown")

                # Map Bandit test IDs to OWASP categories
                owasp = _bandit_to_owasp(test_id)

                results.append({
                    "scanner": "bandit",
                    "rule_id": test_id,
                    "severity": severity,
                    "confidence": issue.get("issue_confidence", "MEDIUM").upper(),
                    "title": issue.get("test_name", test_id),
                    "description": issue.get("issue_text", ""),
                    "file": issue.get("filename", "").replace(target_dir, "").lstrip("/\\"),
                    "line": issue.get("line_number", 0),
                    "code_snippet": issue.get("code", "").strip(),
                    "cwe": issue.get("issue_cwe", {}).get("id", None),
                    "owasp": owasp,
                    "fix": issue.get("more_info", "See Bandit documentation for remediation."),
                })
    except FileNotFoundError:
        pass  # Bandit not installed — skip silently, regex scanner will still work
    except subprocess.TimeoutExpired:
        pass
    except Exception:
        pass
    return results


def _bandit_to_owasp(test_id: str) -> str:
    """Map Bandit test IDs to OWASP Top 10 categories."""
    mapping = {
        "B101": "A05", "B102": "A03", "B103": "A05", "B104": "A05", "B105": "A02",
        "B106": "A02", "B107": "A02", "B108": "A05", "B110": "A09",
        "B201": "A03", "B202": "A03",
        "B301": "A08", "B302": "A08", "B303": "A02", "B304": "A02", "B305": "A02",
        "B306": "A05", "B307": "A05", "B308": "A05", "B309": "A05", "B310": "A10",
        "B311": "A02", "B312": "A10", "B313": "A03", "B314": "A03",
        "B320": "A03", "B321": "A10", "B322": "A03", "B323": "A02", "B324": "A02",
        "B325": "A02",
        "B501": "A02", "B502": "A02", "B503": "A02", "B504": "A02", "B505": "A02",
        "B506": "A03", "B507": "A02", "B508": "A05", "B509": "A05",
        "B601": "A03", "B602": "A03", "B603": "A03", "B604": "A03", "B605": "A03",
        "B606": "A03", "B607": "A03", "B608": "A03", "B609": "A03", "B610": "A03",
        "B611": "A03",
        "B701": "A03", "B702": "A03", "B703": "A03",
    }
    return mapping.get(test_id, "A04")


def run_pattern_scan(target_dir: str) -> list[dict]:
    """Scan all text files for vulnerability patterns across multiple languages."""
    results = []
    text_extensions = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".mjs", ".cjs",
        ".java", ".go", ".rb", ".php", ".c", ".cpp", ".h", ".cs",
        ".env", ".yml", ".yaml", ".json", ".toml", ".cfg", ".ini",
        ".sh", ".bat", ".ps1", ".html", ".css", ".xml", ".sql",
        ".tf", ".dockerfile", ".docker-compose.yml",
    }
    skip_dirs = {"node_modules", ".git", "__pycache__", "venv", ".venv", "env",
                 ".next", "dist", "build", ".cache", "vendor", "target"}

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for filename in files:
            ext = Path(filename).suffix.lower()
            # Also check extensionless files like Dockerfile, Makefile
            if ext not in text_extensions and filename not in {"Dockerfile", "Makefile", ".env", ".gitignore"}:
                continue

            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    for pat in VULN_PATTERNS:
                        if re.search(pat["pattern"], line):
                            results.append({
                                "scanner": "pattern-engine",
                                "rule_id": pat["id"],
                                "severity": pat["severity"],
                                "confidence": "HIGH",
                                "title": pat["title"],
                                "description": pat["description"],
                                "file": filepath.replace(target_dir, "").lstrip("/\\"),
                                "line": line_num,
                                "code_snippet": line.strip()[:150],
                                "cwe": pat.get("cwe"),
                                "owasp": pat.get("owasp", "A04"),
                                "fix": pat.get("fix", "Review and remediate this finding."),
                            })
            except Exception:
                continue
    return results


def extract_upload(upload_path: str, dest_dir: str) -> str:
    """Extract a ZIP file or copy a single file to dest_dir."""
    if zipfile.is_zipfile(upload_path):
        with zipfile.ZipFile(upload_path, 'r') as zf:
            zf.extractall(dest_dir)
        return dest_dir
    else:
        shutil.copy2(upload_path, dest_dir)
        return dest_dir


def compute_severity_stats(vulns: list[dict]) -> dict:
    """Compute severity distribution for the vulnerability list."""
    stats = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for v in vulns:
        sev = v.get("severity", "LOW").upper()
        if sev in stats:
            stats[sev] += 1
        else:
            stats["LOW"] += 1

    # Compute OWASP distribution
    owasp_dist = {}
    for v in vulns:
        cat = v.get("owasp", "A04")
        label = f"{cat}: {OWASP_CATEGORIES.get(cat, 'Other')}"
        owasp_dist[label] = owasp_dist.get(label, 0) + 1

    return {"severity": stats, "owasp": owasp_dist}


def full_scan(target_dir: str) -> tuple[list[dict], dict]:
    """Run all scanners and return combined, deduplicated results + statistics."""
    all_results = []
    all_results.extend(run_bandit_scan(target_dir))
    all_results.extend(run_pattern_scan(target_dir))

    # De-duplicate by (file, line, rule_id)
    seen = set()
    unique = []
    for r in all_results:
        key = (r.get("file", ""), r.get("line", 0), r.get("rule_id", ""))
        if key not in seen:
            seen.add(key)
            unique.append(r)

    # Sort by severity priority
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
    unique.sort(key=lambda x: severity_order.get(x.get("severity", "LOW"), 3))

    stats = compute_severity_stats(unique)
    return unique, stats
