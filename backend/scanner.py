"""
Real vulnerability scanner using Bandit (Python static analysis).
Also includes custom regex-based secret detection for any language.
"""
import subprocess
import json
import re
import os
import tempfile
import zipfile
import shutil
from pathlib import Path


# --- Custom regex patterns for secret/sensitive data detection ---
SECRET_PATTERNS = [
    {"id": "HARDCODED_PASSWORD", "severity": "HIGH", "pattern": r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']', "description": "Hardcoded password found in source code"},
    {"id": "API_KEY_LEAK", "severity": "HIGH", "pattern": r'(?i)(api[_-]?key|apikey|secret[_-]?key)\s*=\s*["\'][A-Za-z0-9_\-]{16,}["\']', "description": "Hardcoded API key or secret key detected"},
    {"id": "AWS_KEY", "severity": "CRITICAL", "pattern": r'AKIA[0-9A-Z]{16}', "description": "AWS Access Key ID found in source code"},
    {"id": "PRIVATE_KEY", "severity": "CRITICAL", "pattern": r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----', "description": "Private key embedded in source code"},
    {"id": "JWT_TOKEN", "severity": "HIGH", "pattern": r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}', "description": "JWT token found hardcoded in source code"},
    {"id": "SQL_INJECTION", "severity": "HIGH", "pattern": r'(?i)(execute|cursor\.execute|query)\s*\(\s*["\'].*%s.*["\']|f["\'].*SELECT.*\{', "description": "Potential SQL injection via string formatting"},
    {"id": "EVAL_USAGE", "severity": "MEDIUM", "pattern": r'\beval\s*\(', "description": "Use of eval() can allow arbitrary code execution"},
    {"id": "EXEC_USAGE", "severity": "MEDIUM", "pattern": r'\bexec\s*\(', "description": "Use of exec() can allow arbitrary code execution"},
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
                results.append({
                    "scanner": "bandit",
                    "rule_id": issue.get("test_id", "unknown"),
                    "severity": issue.get("issue_severity", "MEDIUM").upper(),
                    "confidence": issue.get("issue_confidence", "MEDIUM").upper(),
                    "description": issue.get("issue_text", ""),
                    "file": issue.get("filename", "").replace(target_dir, "").lstrip("/\\"),
                    "line": issue.get("line_number", 0),
                    "code_snippet": issue.get("code", ""),
                    "cwe": issue.get("issue_cwe", {}).get("id", None),
                    "more_info": issue.get("more_info", ""),
                })
    except FileNotFoundError:
        results.append({
            "scanner": "bandit",
            "rule_id": "BANDIT_NOT_FOUND",
            "severity": "INFO",
            "confidence": "HIGH",
            "description": "Bandit scanner not found. Install with: pip install bandit",
            "file": "",
            "line": 0,
            "code_snippet": "",
            "cwe": None,
            "more_info": "",
        })
    except Exception as e:
        results.append({
            "scanner": "bandit",
            "rule_id": "SCAN_ERROR",
            "severity": "INFO",
            "confidence": "HIGH",
            "description": f"Bandit scan encountered an error: {str(e)}",
            "file": "",
            "line": 0,
            "code_snippet": "",
            "cwe": None,
            "more_info": "",
        })
    return results


def run_secret_scan(target_dir: str) -> list[dict]:
    """Scan all text files for hardcoded secrets and dangerous patterns."""
    results = []
    text_extensions = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rb", ".php", ".env", ".yml", ".yaml", ".json", ".toml", ".cfg", ".ini", ".sh", ".bat", ".ps1", ".html", ".css"}
    
    for root, dirs, files in os.walk(target_dir):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".git", "__pycache__", "venv", ".venv", "env"}]
        
        for filename in files:
            ext = Path(filename).suffix.lower()
            if ext not in text_extensions:
                continue
            
            filepath = os.path.join(root, filename)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    for pattern_info in SECRET_PATTERNS:
                        if re.search(pattern_info["pattern"], line):
                            results.append({
                                "scanner": "secret-detector",
                                "rule_id": pattern_info["id"],
                                "severity": pattern_info["severity"],
                                "confidence": "HIGH",
                                "description": pattern_info["description"],
                                "file": filepath.replace(target_dir, "").lstrip("/\\"),
                                "line": line_num,
                                "code_snippet": line.strip()[:120],
                                "cwe": None,
                                "more_info": "",
                            })
            except Exception:
                continue
    return results


def extract_upload(upload_path: str, dest_dir: str) -> str:
    """Extract a ZIP file or copy a single file to dest_dir. Returns the scan target path."""
    if zipfile.is_zipfile(upload_path):
        with zipfile.ZipFile(upload_path, 'r') as zf:
            zf.extractall(dest_dir)
        return dest_dir
    else:
        # Single file — just copy it
        shutil.copy2(upload_path, dest_dir)
        return dest_dir


def full_scan(target_dir: str) -> list[dict]:
    """Run all scanners and return combined results."""
    all_results = []
    all_results.extend(run_bandit_scan(target_dir))
    all_results.extend(run_secret_scan(target_dir))
    
    # De-duplicate by (file, line, rule_id)
    seen = set()
    unique = []
    for r in all_results:
        key = (r["file"], r["line"], r["rule_id"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    
    return unique
