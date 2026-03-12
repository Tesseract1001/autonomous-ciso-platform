"""
Autonomous Secure Software Intelligence & Assurance Platform
Main FastAPI Application — Real version with file upload, Bandit scanning, and AI reasoning.
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
    description="Autonomous Secure Software Intelligence & Assurance Platform",
    version="1.0.0",
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
    return {"status": "Virtual CISO Intelligence Engine is ONLINE", "version": "1.0.0"}


@app.post("/api/scan/upload")
async def scan_uploaded_file(file: UploadFile = File(...)):
    """
    Upload a ZIP file or a single source code file.
    The system will:
    1. Extract it
    2. Run Bandit (Python static analysis) on it
    3. Run custom secret / vulnerability detection
    4. Feed results into the AI reasoning engine (Gemini or local)
    5. Generate exploit chains, risk score, and executive summary
    6. Cryptographically sign the report
    """
    start_time = time.time()
    
    # Save uploaded file to a temp location
    tmp_dir = tempfile.mkdtemp(prefix="ciso_scan_")
    upload_path = os.path.join(tmp_dir, file.filename or "upload.zip")
    
    try:
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Extract if ZIP, otherwise just use the temp dir
        scan_dir = os.path.join(tmp_dir, "extracted")
        os.makedirs(scan_dir, exist_ok=True)
        extract_upload(upload_path, scan_dir)
        
        # STEP 1: Run real scanners
        raw_vulnerabilities = full_scan(scan_dir)
        
        # STEP 2: Feed into AI reasoning engine
        intelligence_report = generate_intelligence_report(raw_vulnerabilities)
        
        # STEP 3: Sign the report cryptographically
        report_json = json.dumps(intelligence_report, sort_keys=True).encode("utf-8")
        signature = hashlib.sha256(report_json).hexdigest()
        
        scan_time = round(time.time() - start_time, 2)
        
        return {
            "success": True,
            "scan_time_seconds": scan_time,
            "total_vulnerabilities": len(raw_vulnerabilities),
            "raw_vulnerabilities": raw_vulnerabilities,
            "intelligence_report": intelligence_report,
            "signature": signature,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
    finally:
        # Cleanup temp files
        shutil.rmtree(tmp_dir, ignore_errors=True)


@app.post("/api/scan/code")
async def scan_pasted_code(code: str = Form(...), filename: str = Form(default="uploaded_code.py")):
    """
    Paste source code directly. The system will scan it as if it were a file.
    """
    start_time = time.time()
    tmp_dir = tempfile.mkdtemp(prefix="ciso_paste_")
    
    try:
        # Write pasted code to a temp file
        code_path = os.path.join(tmp_dir, filename)
        with open(code_path, "w", encoding="utf-8") as f:
            f.write(code)
        
        # STEP 1: Run real scanners
        raw_vulnerabilities = full_scan(tmp_dir)
        
        # STEP 2: AI reasoning
        intelligence_report = generate_intelligence_report(raw_vulnerabilities)
        
        # STEP 3: Sign the report
        report_json = json.dumps(intelligence_report, sort_keys=True).encode("utf-8")
        signature = hashlib.sha256(report_json).hexdigest()
        
        scan_time = round(time.time() - start_time, 2)
        
        return {
            "success": True,
            "scan_time_seconds": scan_time,
            "total_vulnerabilities": len(raw_vulnerabilities),
            "raw_vulnerabilities": raw_vulnerabilities,
            "intelligence_report": intelligence_report,
            "signature": signature,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
