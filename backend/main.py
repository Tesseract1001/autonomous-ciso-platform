from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib

app = FastAPI(title="Virtual CISO Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    repository_url: str

class IntelligenceReport(BaseModel):
    risk_score: int
    executive_summary: str
    exploit_chains: list
    signature: str

@app.get("/")
def read_root():
    return {"status": "Virtual CISO Engine is running"}

@app.post("/api/scan", response_model=IntelligenceReport)
def run_autonomous_scan(request: ScanRequest):
    # This is where we will simulate the intelligence reasoning
    # and generate the exploit chains.
    
    report_data = {
        "risk_score": 92,
        "executive_summary": "CRITICAL RISK DETECTED: A combination of a leaked API key and weak database access controls exposes the entire customer database to public access. Immediate remediation required.",
        "exploit_chains": [
            {
                "id": "chain-1",
                "nodes": [
                    {"id": "node-1", "label": "Leaked API Key discovered in public repo"},
                    {"id": "node-2", "label": "Bypass Authentication via API"},
                    {"id": "node-3", "label": "Database Dump (SQL Injection on inner endpoint)"}
                ],
                "edges": [
                    {"source": "node-1", "target": "node-2"},
                    {"source": "node-2", "target": "node-3"}
                ]
            }
        ]
    }
    
    # Generate the cryptographic signature for the tamper-evident audit trail
    report_string = str(report_data).encode('utf-8')
    signature = hashlib.sha256(report_string).hexdigest()
    
    return IntelligenceReport(
        risk_score=report_data["risk_score"],
        executive_summary=report_data["executive_summary"],
        exploit_chains=report_data["exploit_chains"],
        signature=signature
    )
