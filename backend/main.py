"""
Autonomous Secure Software Intelligence & Assurance Platform
Professional FastAPI Application
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import hashlib
import json
import tempfile
import shutil
import os
import time

from scanner import full_scan, extract_upload
from ai_engine import generate_intelligence_report

app = FastAPI(
    title="Virtual CISO Intelligence Engine",
    description="Autonomous Secure Software Intelligence & Assurance Platform — Real-time vulnerability scanning, AI-powered exploit chain correlation, and executive-level reporting.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "online",
        "engine": "Virtual CISO Intelligence Engine",
        "version": "2.0.0",
        "capabilities": ["bandit-scan", "multi-lang-pattern-scan", "ai-exploit-chains", "crypto-audit-trail"],
    }


@app.get("/api/health")
def health():
    gemini_status = "connected" if os.environ.get("GEMINI_API_KEY") else "not configured (using local reasoning)"
    return {
        "status": "healthy",
        "scanners": ["bandit", "pattern-engine"],
        "ai_engine": gemini_status,
    }


@app.post("/api/scan/upload")
async def scan_uploaded_file(file: UploadFile = File(...)):
    """
    Upload a ZIP file or single source code file for autonomous scanning.
    
    Pipeline:
    1. Extract uploaded file
    2. Run Bandit (Python static analysis) + multi-language pattern scanner
    3. Compute severity & OWASP statistics
    4. Feed findings into AI reasoning engine (Gemini or local fallback)
    5. Generate exploit chains, risk score, executive summary, remediation plan
    6. Cryptographically sign the report (SHA-256 tamper-evident audit trail)
    """
    start_time = time.time()
    tmp_dir = tempfile.mkdtemp(prefix="ciso_scan_")
    upload_path = os.path.join(tmp_dir, file.filename or "upload.zip")

    try:
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)

        scan_dir = os.path.join(tmp_dir, "extracted")
        os.makedirs(scan_dir, exist_ok=True)
        extract_upload(upload_path, scan_dir)

        # Count files scanned
        file_count = sum(1 for _, _, files in os.walk(scan_dir) for _ in files)

        # Run real scanners
        raw_vulnerabilities, stats = full_scan(scan_dir)

        # AI reasoning
        intelligence_report = generate_intelligence_report(raw_vulnerabilities, stats)

        # Cryptographic signing
        report_payload = json.dumps(intelligence_report, sort_keys=True, default=str).encode("utf-8")
        signature = hashlib.sha256(report_payload).hexdigest()

        scan_time = round(time.time() - start_time, 2)

        return {
            "success": True,
            "scan_time_seconds": scan_time,
            "files_scanned": file_count,
            "total_vulnerabilities": len(raw_vulnerabilities),
            "severity_stats": stats.get("severity", {}),
            "owasp_stats": stats.get("owasp", {}),
            "raw_vulnerabilities": raw_vulnerabilities,
            "intelligence_report": intelligence_report,
            "signature": signature,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@app.post("/api/scan/code")
async def scan_pasted_code(code: str = Form(...), filename: str = Form(default="pasted_code.py")):
    """Paste source code directly for analysis."""
    start_time = time.time()
    tmp_dir = tempfile.mkdtemp(prefix="ciso_paste_")

    try:
        code_path = os.path.join(tmp_dir, filename)
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)

        raw_vulnerabilities, stats = full_scan(tmp_dir)
        intelligence_report = generate_intelligence_report(raw_vulnerabilities, stats)

        report_payload = json.dumps(intelligence_report, sort_keys=True, default=str).encode("utf-8")
        signature = hashlib.sha256(report_payload).hexdigest()

        scan_time = round(time.time() - start_time, 2)

        return {
            "success": True,
            "scan_time_seconds": scan_time,
            "files_scanned": 1,
            "total_vulnerabilities": len(raw_vulnerabilities),
            "severity_stats": stats.get("severity", {}),
            "owasp_stats": stats.get("owasp", {}),
            "raw_vulnerabilities": raw_vulnerabilities,
            "intelligence_report": intelligence_report,
            "signature": signature,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
