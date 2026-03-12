"""
Professional AI Reasoning Engine — Gemini Integration
Generates OWASP-mapped exploit chains, executive CISO summaries,
and prioritized remediation plans from real vulnerability scan data.
"""
import json
import os

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

SYSTEM_PROMPT = """You are a world-class Chief Information Security Officer (CISO) AI.

You receive REAL vulnerability scan results from Bandit (Python static analysis) and a custom multi-language pattern scanner. These are REAL findings from actual source code — not hypothetical.

Your task:
1. Analyze ALL vulnerabilities together. Look for connections.
2. Identify EXPLOIT CHAINS: sequences where 2+ weaknesses combine for a bigger attack.
   Example: Hardcoded API key (SECRET-002) + CORS wildcard (ACCESS-002) + SQL injection (INJ-001) = An external attacker uses the API key from the public repo to bypass auth, exploits the SQL injection to dump the database, and CORS allows exfiltration to their domain.
3. Map each chain to OWASP Top 10 (2021) categories.
4. Assign an OVERALL RISK SCORE (0-100). Use this scale:
   - 0-20: Low risk, minor issues only
   - 21-40: Moderate risk, some concerning findings
   - 41-60: High risk, significant vulnerabilities present
   - 61-80: Critical risk, exploitable chains detected
   - 81-100: Severe risk, immediate action required
5. Write an EXECUTIVE SUMMARY (3-5 sentences) a non-technical CEO can understand. Focus on BUSINESS IMPACT: data breach, financial loss, regulatory fines, reputation damage.
6. Create REMEDIATION PRIORITIES ranked by urgency.

IMPORTANT RULES:
- Be specific. Reference exact files and line numbers from the scan data.
- If findings are all LOW/INFO, still provide useful analysis but assign a low risk score.
- Every exploit chain must have at least 2 nodes connected by edges.
- Generate AT LEAST 1 exploit chain, even for minor findings (show the potential attack path).

Respond ONLY with this exact JSON structure:
{
  "risk_score": <integer 0-100>,
  "risk_level": "CRITICAL|HIGH|MEDIUM|LOW",
  "executive_summary": "<3-5 sentences for a CEO>",
  "findings_summary": "<technical summary>",
  "exploit_chains": [
    {
      "chain_name": "<attack scenario name>",
      "impact": "CRITICAL|HIGH|MEDIUM|LOW",
      "owasp_categories": ["A01", "A03"],
      "description": "<how attacker chains these vulnerabilities>",
      "business_impact": "<what the business loses>",
      "nodes": [
        {"id": "node-1", "label": "<vulnerability name>", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "file": "<filename>", "line": <number>},
        {"id": "node-2", "label": "<next step in attack>", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "file": "<filename>", "line": <number>}
      ],
      "edges": [
        {"source": "node-1", "target": "node-2", "label": "<how node-1 enables node-2>"}
      ]
    }
  ],
  "remediation_priorities": [
    {"priority": 1, "action": "<specific fix>", "file": "<filename>", "severity": "CRITICAL", "reason": "<why this is urgent>", "effort": "LOW|MEDIUM|HIGH"},
    {"priority": 2, "action": "<next fix>", "file": "<filename>", "severity": "HIGH", "reason": "<why>", "effort": "LOW|MEDIUM|HIGH"}
  ],
  "compliance_notes": "<brief note on OWASP, PCI-DSS, GDPR, SOC2 implications if relevant>"
}
"""


def generate_intelligence_report(vulnerabilities: list[dict], stats: dict) -> dict:
    """Feed real scan results into Gemini AI and get back a structured intelligence report."""

    vuln_summary = json.dumps(vulnerabilities, indent=2, default=str)
    stats_summary = json.dumps(stats, indent=2)

    user_prompt = f"""Analyze these REAL vulnerability scan results and generate the intelligence report.

SCAN STATISTICS:
{stats_summary}

DETAILED FINDINGS ({len(vulnerabilities)} total):
{vuln_summary}
"""

    if GENAI_AVAILABLE and GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=user_prompt,
                config={
                    "system_instruction": SYSTEM_PROMPT,
                    "temperature": 0.2,
                    "response_mime_type": "application/json",
                }
            )

            result_text = response.text.strip()
            if result_text.startswith("```"):
                result_text = result_text.split("\n", 1)[1]
                if result_text.endswith("```"):
                    result_text = result_text.rsplit("```", 1)[0]

            parsed = json.loads(result_text)

            # Ensure required fields exist
            parsed.setdefault("risk_score", 50)
            parsed.setdefault("risk_level", "MEDIUM")
            parsed.setdefault("executive_summary", "Analysis complete.")
            parsed.setdefault("findings_summary", "")
            parsed.setdefault("exploit_chains", [])
            parsed.setdefault("remediation_priorities", [])
            parsed.setdefault("compliance_notes", "")

            return parsed

        except Exception as e:
            print(f"[AI Engine] Gemini API error: {e}. Falling back to local reasoning.")
            return _local_reasoning(vulnerabilities, stats)
    else:
        if not GEMINI_API_KEY:
            print("[AI Engine] No GEMINI_API_KEY set. Using local reasoning engine.")
            print("[AI Engine] Set your key: $env:GEMINI_API_KEY = 'your-key-here'")
        return _local_reasoning(vulnerabilities, stats)


def _local_reasoning(vulnerabilities: list[dict], stats: dict) -> dict:
    """Intelligent local fallback that creates proper exploit chains without AI."""
    if not vulnerabilities:
        return {
            "risk_score": 5,
            "risk_level": "LOW",
            "executive_summary": "No significant security vulnerabilities were detected in the scanned codebase. The application follows secure coding practices based on the analyzed files.",
            "findings_summary": "Static analysis and pattern scanning returned zero findings.",
            "exploit_chains": [],
            "remediation_priorities": [],
            "compliance_notes": "No significant compliance concerns identified.",
        }

    # Calculate risk score
    severity_weights = {"CRITICAL": 25, "HIGH": 15, "MEDIUM": 8, "LOW": 3, "INFO": 1}
    total_weight = sum(severity_weights.get(v.get("severity", "LOW"), 3) for v in vulnerabilities)
    risk_score = min(100, max(5, total_weight))

    risk_level = "LOW"
    if risk_score > 80: risk_level = "CRITICAL"
    elif risk_score > 60: risk_level = "HIGH"
    elif risk_score > 40: risk_level = "MEDIUM"

    # Categorize vulnerabilities
    critical = [v for v in vulnerabilities if v.get("severity") == "CRITICAL"]
    high = [v for v in vulnerabilities if v.get("severity") == "HIGH"]
    medium = [v for v in vulnerabilities if v.get("severity") == "MEDIUM"]
    secrets = [v for v in vulnerabilities if v.get("rule_id", "").startswith("SECRET")]
    injections = [v for v in vulnerabilities if v.get("rule_id", "").startswith("INJ") or v.get("owasp") == "A03"]
    crypto = [v for v in vulnerabilities if v.get("owasp") == "A02" and not v.get("rule_id", "").startswith("SECRET")]

    # Build intelligent exploit chains
    chains = []
    node_counter = [1]

    def make_node(v):
        nid = f"node-{node_counter[0]}"
        node_counter[0] += 1
        return {"id": nid, "label": v.get("title", v.get("description", ""))[:60], "severity": v.get("severity", "MEDIUM"), "file": v.get("file", ""), "line": v.get("line", 0)}

    # Chain: Credential Leak → System Compromise
    if secrets and injections:
        nodes = [make_node(secrets[0])]
        edges = []
        if len(secrets) > 1:
            n = make_node(secrets[1])
            nodes.append(n)
            edges.append({"source": nodes[0]["id"], "target": n["id"], "label": "Multiple credentials exposed"})
        inj = make_node(injections[0])
        nodes.append(inj)
        edges.append({"source": nodes[-2]["id"], "target": inj["id"], "label": "Bypass auth using leaked credentials"})
        impact_node = {"id": f"node-{node_counter[0]}", "label": "Full Database Compromise", "severity": "CRITICAL", "file": "", "line": 0}
        node_counter[0] += 1
        nodes.append(impact_node)
        edges.append({"source": inj["id"], "target": impact_node["id"], "label": "Execute injection to dump data"})

        chains.append({
            "chain_name": "Credential Leak → Injection → Data Breach",
            "impact": "CRITICAL",
            "owasp_categories": ["A02", "A03"],
            "description": f"Hardcoded credentials in {secrets[0].get('file', 'source')} provide authentication bypass. Combined with {injections[0].get('title', 'injection vulnerability')}, an attacker achieves full database access.",
            "business_impact": "Complete customer data breach. Regulatory fines under GDPR/CCPA. Reputation damage.",
            "nodes": nodes,
            "edges": edges,
        })

    # Chain: Code Execution
    code_exec = [v for v in vulnerabilities if v.get("rule_id") in ("INJ-004", "INJ-005", "DESER-001", "DESER-002")]
    if code_exec:
        nodes = []
        edges = []
        for i, v in enumerate(code_exec[:3]):
            nodes.append(make_node(v))
        rce_node = {"id": f"node-{node_counter[0]}", "label": "Remote Code Execution (RCE)", "severity": "CRITICAL", "file": "", "line": 0}
        node_counter[0] += 1
        nodes.append(rce_node)
        for i in range(len(nodes) - 1):
            edges.append({"source": nodes[i]["id"], "target": nodes[i+1]["id"], "label": "enables" if i < len(nodes) - 2 else "achieves RCE"})

        chains.append({
            "chain_name": "Unsafe Code Execution Path",
            "impact": "CRITICAL",
            "owasp_categories": ["A03", "A08"],
            "description": "Usage of eval(), exec(), or insecure deserialization creates direct paths to remote code execution.",
            "business_impact": "Attacker gains full server control. Can install ransomware, exfiltrate all data, or pivot to internal network.",
            "nodes": nodes, "edges": edges,
        })

    # Chain: Crypto failures
    if secrets and crypto:
        nodes = [make_node(secrets[0]), make_node(crypto[0])]
        impact = {"id": f"node-{node_counter[0]}", "label": "Credential Compromise at Scale", "severity": "HIGH", "file": "", "line": 0}
        node_counter[0] += 1
        nodes.append(impact)
        edges = [
            {"source": nodes[0]["id"], "target": nodes[1]["id"], "label": "credentials stored with weak crypto"},
            {"source": nodes[1]["id"], "target": impact["id"], "label": "hashes cracked in minutes"},
        ]
        chains.append({
            "chain_name": "Weak Cryptography → Mass Credential Theft",
            "impact": "HIGH",
            "owasp_categories": ["A02"],
            "description": "Secrets are protected with broken algorithms (MD5/SHA-1). An attacker who obtains the hashes can crack them using rainbow tables in seconds.",
            "business_impact": "All user passwords compromised. Account takeover at scale.",
            "nodes": nodes, "edges": edges,
        })

    # Catch-all chain for remaining
    if not chains and vulnerabilities:
        nodes = []
        edges = []
        for v in vulnerabilities[:4]:
            nodes.append(make_node(v))
        for i in range(len(nodes) - 1):
            edges.append({"source": nodes[i]["id"], "target": nodes[i+1]["id"], "label": "combined with"})
        chains.append({
            "chain_name": "Multi-Vector Attack Surface",
            "impact": "HIGH" if high else "MEDIUM",
            "owasp_categories": list(set(v.get("owasp", "A04") for v in vulnerabilities[:4])),
            "description": "Multiple vulnerabilities across the codebase create an expanded attack surface that could be exploited in combination.",
            "business_impact": "Increased risk of targeted attacks exploiting multiple weaknesses simultaneously.",
            "nodes": nodes, "edges": edges,
        })

    # Executive summary
    parts = []
    if critical: parts.append(f"{len(critical)} CRITICAL vulnerabilities requiring immediate action")
    if high: parts.append(f"{len(high)} HIGH severity issues")
    if medium: parts.append(f"{len(medium)} MEDIUM severity findings")

    executive_summary = f"Security analysis detected {len(vulnerabilities)} vulnerabilities across the codebase. "
    if parts:
        executive_summary += ". ".join(parts) + ". "
    if secrets:
        executive_summary += f"Most critically, {len(secrets)} hardcoded secrets were found — these provide direct access to systems if the source code is exposed. "
    if injections:
        executive_summary += f"Additionally, {len(injections)} injection vulnerabilities were detected that could allow attackers to execute arbitrary commands or queries. "
    executive_summary += "Immediate remediation is strongly recommended to prevent a potential data breach."

    # Remediation priorities
    priorities = []
    sorted_vulns = sorted(vulnerabilities, key=lambda x: severity_weights.get(x.get("severity", "LOW"), 0), reverse=True)
    for i, v in enumerate(sorted_vulns[:5]):
        priorities.append({
            "priority": i + 1,
            "action": v.get("fix", f"Fix {v.get('title', v.get('rule_id', 'unknown'))}"),
            "file": v.get("file", ""),
            "severity": v.get("severity", "MEDIUM"),
            "reason": v.get("description", "Security risk identified."),
            "effort": "LOW" if v.get("severity") in ("CRITICAL", "HIGH") else "MEDIUM",
        })

    # Compliance notes
    owasp_cats_found = set(v.get("owasp", "") for v in vulnerabilities if v.get("owasp"))
    compliance = f"Findings map to OWASP Top 10 categories: {', '.join(sorted(owasp_cats_found))}. "
    if "A02" in owasp_cats_found or "A03" in owasp_cats_found:
        compliance += "PCI-DSS compliance is at risk due to cryptographic and injection findings. "
    if secrets:
        compliance += "GDPR Article 32 requires appropriate technical measures to protect personal data — hardcoded credentials violate this requirement."

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "executive_summary": executive_summary,
        "findings_summary": f"Found {len(vulnerabilities)} issues: {len(critical)} critical, {len(high)} high, {len(medium)} medium severity.",
        "exploit_chains": chains,
        "remediation_priorities": priorities,
        "compliance_notes": compliance,
    }
