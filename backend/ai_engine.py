"""
AI Reasoning Engine — uses Google Gemini to correlate raw vulnerabilities
into exploit chains and generate executive-level CISO summaries.
"""
import json
import os

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

SYSTEM_PROMPT = """You are a world-class Chief Information Security Officer (CISO) AI assistant.
You are given a list of real vulnerabilities found by automated static analysis scanners in a codebase.

Your job is to:
1. Analyze ALL the vulnerabilities together as a whole.
2. Identify "Exploit Chains" — sequences where an attacker could combine 2 or more weaknesses to achieve a larger attack. 
   For example: a hardcoded API key + an unprotected admin endpoint = full database access.
3. Assign an overall RISK SCORE from 0 to 100 (100 = extremely dangerous).
4. Write a short but powerful EXECUTIVE SUMMARY explaining the business impact in simple terms a CEO would understand.
5. For EACH exploit chain, list the nodes (vulnerabilities) and edges (how they connect).

You MUST respond in this exact JSON format and nothing else:

{
  "risk_score": <integer 0-100>,
  "executive_summary": "<2-3 sentences explaining the overall risk in business terms>",
  "findings_summary": "<brief technical summary of what was found>",
  "exploit_chains": [
    {
      "chain_name": "<name of the attack scenario>",
      "impact": "CRITICAL|HIGH|MEDIUM|LOW",
      "description": "<how the attacker chains these together>",
      "nodes": [
        {"id": "node-1", "label": "<short vulnerability name>", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "file": "<filename>", "line": <line_number>},
        {"id": "node-2", "label": "<short vulnerability name>", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "file": "<filename>", "line": <line_number>}
      ],
      "edges": [
        {"source": "node-1", "target": "node-2", "label": "<how node-1 enables node-2>"}
      ]
    }
  ],
  "remediation_priorities": [
    {"priority": 1, "action": "<what to fix first>", "reason": "<why this is most urgent>"},
    {"priority": 2, "action": "<what to fix second>", "reason": "<why>"}
  ]
}

If there are only 1 or 2 minor vulnerabilities and no real chain is possible, still create a single chain showing the individual risk path. Always return valid JSON.
"""


def generate_intelligence_report(vulnerabilities: list[dict]) -> dict:
    """Feed real scan results into Gemini AI and get back a structured intelligence report."""
    
    # Format vulnerabilities for the AI
    vuln_text = json.dumps(vulnerabilities, indent=2)
    user_prompt = f"""Here are the real vulnerability scan results from the codebase. Analyze them and generate the intelligence report:

{vuln_text}
"""

    # Try to use Gemini API
    if GENAI_AVAILABLE and GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=user_prompt,
                config={
                    "system_instruction": SYSTEM_PROMPT,
                    "temperature": 0.3,
                    "response_mime_type": "application/json",
                }
            )
            
            result_text = response.text.strip()
            # Clean markdown code fences if present
            if result_text.startswith("```"):
                result_text = result_text.split("\n", 1)[1]
                if result_text.endswith("```"):
                    result_text = result_text.rsplit("```", 1)[0]
            
            return json.loads(result_text)
            
        except Exception as e:
            print(f"Gemini API error: {e}. Falling back to local reasoning.")
            return _local_reasoning(vulnerabilities)
    else:
        print("Gemini API not configured. Using local reasoning engine.")
        return _local_reasoning(vulnerabilities)


def _local_reasoning(vulnerabilities: list[dict]) -> dict:
    """Fallback: generate a reasonable intelligence report without AI when no API key is available."""
    if not vulnerabilities:
        return {
            "risk_score": 5,
            "executive_summary": "No significant vulnerabilities were detected in the scanned codebase. The application appears to follow secure coding practices.",
            "findings_summary": "Static analysis and secret detection scans returned zero findings.",
            "exploit_chains": [],
            "remediation_priorities": [],
        }
    
    # Calculate risk score based on severity counts
    severity_weights = {"CRITICAL": 25, "HIGH": 15, "MEDIUM": 8, "LOW": 3, "INFO": 1}
    total_weight = sum(severity_weights.get(v.get("severity", "LOW"), 3) for v in vulnerabilities)
    risk_score = min(100, total_weight)
    
    # Group by severity
    critical = [v for v in vulnerabilities if v.get("severity") == "CRITICAL"]
    high = [v for v in vulnerabilities if v.get("severity") == "HIGH"]
    medium = [v for v in vulnerabilities if v.get("severity") == "MEDIUM"]
    
    # Build exploit chains from related vulnerabilities
    chains = []
    node_counter = 1
    
    # Chain 1: If there are secrets + any other vulnerability
    secret_vulns = [v for v in vulnerabilities if v.get("scanner") == "secret-detector"]
    code_vulns = [v for v in vulnerabilities if v.get("scanner") == "bandit"]
    
    if secret_vulns and code_vulns:
        nodes = []
        edges = []
        for i, v in enumerate(secret_vulns[:2]):
            node_id = f"node-{node_counter}"
            nodes.append({"id": node_id, "label": v["description"][:50], "severity": v["severity"], "file": v["file"], "line": v["line"]})
            node_counter += 1
        for i, v in enumerate(code_vulns[:2]):
            node_id = f"node-{node_counter}"
            nodes.append({"id": node_id, "label": v["description"][:50], "severity": v["severity"], "file": v["file"], "line": v["line"]})
            node_counter += 1
        
        for i in range(len(nodes) - 1):
            edges.append({"source": nodes[i]["id"], "target": nodes[i+1]["id"], "label": "enables access to"})
        
        chains.append({
            "chain_name": "Credential Leak to System Compromise",
            "impact": "CRITICAL" if critical else "HIGH",
            "description": "Leaked credentials combined with code vulnerabilities create a direct path to system compromise.",
            "nodes": nodes,
            "edges": edges,
        })
    elif vulnerabilities:
        nodes = []
        edges = []
        for i, v in enumerate(vulnerabilities[:4]):
            node_id = f"node-{node_counter}"
            nodes.append({"id": node_id, "label": v["description"][:50], "severity": v["severity"], "file": v["file"], "line": v["line"]})
            node_counter += 1
        for i in range(len(nodes) - 1):
            edges.append({"source": nodes[i]["id"], "target": nodes[i+1]["id"], "label": "combined with"})
        
        chains.append({
            "chain_name": "Multi-Vector Attack Surface",
            "impact": "HIGH" if high else "MEDIUM",
            "description": "Multiple vulnerabilities across the codebase create an expanded attack surface.",
            "nodes": nodes,
            "edges": edges,
        })
    
    # Executive summary
    exec_parts = []
    if critical:
        exec_parts.append(f"{len(critical)} CRITICAL vulnerabilities require immediate attention")
    if high:
        exec_parts.append(f"{len(high)} HIGH severity issues detected")
    if medium:
        exec_parts.append(f"{len(medium)} MEDIUM severity findings")
    
    executive_summary = f"Security analysis found {len(vulnerabilities)} total vulnerabilities. " + ". ".join(exec_parts) + ". Immediate remediation is recommended to prevent potential data breaches."
    
    # Priorities
    priorities = []
    for i, v in enumerate(sorted(vulnerabilities, key=lambda x: severity_weights.get(x.get("severity", "LOW"), 0), reverse=True)[:3]):
        priorities.append({
            "priority": i + 1,
            "action": f"Fix {v['rule_id']} in {v['file']}:{v['line']}",
            "reason": v["description"],
        })
    
    return {
        "risk_score": risk_score,
        "executive_summary": executive_summary,
        "findings_summary": f"Found {len(vulnerabilities)} issues: {len(critical)} critical, {len(high)} high, {len(medium)} medium severity.",
        "exploit_chains": chains,
        "remediation_priorities": priorities,
    }
