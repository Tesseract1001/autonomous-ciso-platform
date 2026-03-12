"use client";

import { useState, useRef } from 'react';
import {
  Activity, ShieldAlert, GitBranch, Crosshair,
  Loader2, CheckCircle2, Upload, FileCode, AlertTriangle,
  ClipboardPaste, X, Clock, FileSearch, Shield, ChevronDown, ChevronUp
} from 'lucide-react';
import { StatCard } from './StatCard';
import { ExploitFlow } from './ExploitFlow';
import { RiskGauge } from './RiskGauge';
import { SeverityChart } from './SeverityChart';
import { motion, AnimatePresence } from 'framer-motion';

type ScanMode = "upload" | "paste";

export default function Dashboard() {
  const [isScanning, setIsScanning] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [scanMode, setScanMode] = useState<ScanMode>("upload");
  const [pastedCode, setPastedCode] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [showRawFindings, setShowRawFindings] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const selectedFileRef = useRef<File | null>(null);

  const handleFileSelect = (file: File) => {
    selectedFileRef.current = file;
    setFileName(file.name);
    setError(null);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelect(file);
  };

  const handleScan = async () => {
    setIsScanning(true);
    setReport(null);
    setError(null);

    try {
      let res: Response;

      if (scanMode === "upload") {
        if (!selectedFileRef.current) {
          setError("Please select a file or ZIP to scan.");
          setIsScanning(false);
          return;
        }
        const formData = new FormData();
        formData.append("file", selectedFileRef.current);
        res = await fetch("http://localhost:8000/api/scan/upload", {
          method: "POST",
          body: formData,
        });
      } else {
        if (!pastedCode.trim()) {
          setError("Please paste some source code to scan.");
          setIsScanning(false);
          return;
        }
        const formData = new FormData();
        formData.append("code", pastedCode);
        formData.append("filename", "pasted_code.py");
        res = await fetch("http://localhost:8000/api/scan/code", {
          method: "POST",
          body: formData,
        });
      }

      if (res.ok) {
        const data = await res.json();
        setReport(data);
      } else {
        const errData = await res.json().catch(() => null);
        throw new Error(errData?.detail || `Server returned ${res.status}`);
      }
    } catch (e: any) {
      setError(e.message || "Failed to connect to the Intelligence Engine. Ensure the backend is running on port 8000.");
    } finally {
      setIsScanning(false);
    }
  };

  const ir = report?.intelligence_report;

  return (
    <div className="p-4 lg:p-8 max-w-[1440px] mx-auto">
      {/* ===== HEADER ===== */}
      <header className="mb-8 border-b border-white/10 pb-5 flex flex-col sm:flex-row justify-between sm:items-end gap-4">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <Shield className="w-7 h-7 text-[var(--color-neon-blue)]" />
            <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white">
              <span className="text-glow-blue">CISO</span> Intelligence Platform
            </h1>
          </div>
          <p className="text-gray-500 text-sm ml-10">Autonomous Vulnerability Analysis • Exploit Chain Correlation • Executive Reporting</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 bg-white/5 rounded-lg border border-white/10 text-[10px] font-mono text-gray-400">
            ENGINE v2.0
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[var(--color-neon-green)] animate-pulse" />
            <span className="text-xs font-mono text-[var(--color-neon-green)] uppercase">Online</span>
          </div>
        </div>
      </header>

      {/* ===== UPLOAD SECTION ===== */}
      <motion.div 
        className="glass-panel p-6 mb-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4 flex items-center gap-2">
          <FileSearch className="w-4 h-4 text-[var(--color-neon-blue)]" /> Submit Code for Analysis
        </h2>

        <div className="flex items-center gap-3 mb-4">
          <button
            onClick={() => setScanMode("upload")}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer ${
              scanMode === "upload" ? "bg-[var(--color-neon-blue)]/10 text-[var(--color-neon-blue)] border border-[var(--color-neon-blue)]/30" : "text-gray-500 hover:text-gray-300"
            }`}
          >
            <Upload className="w-4 h-4" /> Upload File / ZIP
          </button>
          <button
            onClick={() => setScanMode("paste")}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer ${
              scanMode === "paste" ? "bg-[var(--color-neon-blue)]/10 text-[var(--color-neon-blue)] border border-[var(--color-neon-blue)]/30" : "text-gray-500 hover:text-gray-300"
            }`}
          >
            <ClipboardPaste className="w-4 h-4" /> Paste Code
          </button>
        </div>

        {scanMode === "upload" ? (
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${
              dragOver
                ? "border-[var(--color-neon-blue)] bg-[var(--color-neon-blue)]/5"
                : fileName
                  ? "border-[var(--color-neon-green)]/40 bg-[var(--color-neon-green)]/5"
                  : "border-white/10 hover:border-white/25 hover:bg-white/[0.02]"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".py,.js,.ts,.zip,.jsx,.tsx,.java,.go,.php,.rb,.env,.yml,.yaml,.json,.c,.cpp,.cs,.sh"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFileSelect(file);
              }}
            />
            {fileName ? (
              <div className="flex items-center justify-center gap-4">
                <FileCode className="w-10 h-10 text-[var(--color-neon-green)]" />
                <div className="text-left">
                  <p className="text-white font-semibold text-lg">{fileName}</p>
                  <p className="text-xs text-gray-400">Ready for autonomous scanning</p>
                </div>
                <button onClick={(e) => { e.stopPropagation(); setFileName(null); selectedFileRef.current = null; }}
                  className="ml-4 p-2 hover:bg-white/10 rounded-lg transition-colors cursor-pointer">
                  <X className="w-4 h-4 text-gray-500 hover:text-white" />
                </button>
              </div>
            ) : (
              <div>
                <Upload className="w-12 h-12 mx-auto text-gray-600 mb-4" />
                <p className="text-gray-300 font-medium text-lg">Drop source code or ZIP here</p>
                <p className="text-xs text-gray-500 mt-2">Python, JavaScript, TypeScript, Java, Go, PHP, Ruby, Shell, Config files</p>
              </div>
            )}
          </div>
        ) : (
          <textarea
            value={pastedCode}
            onChange={(e) => setPastedCode(e.target.value)}
            placeholder={"# Paste your source code here...\n# The scanner will analyze it for vulnerabilities\n\nimport os\npassword = 'admin123'  # Try pasting vulnerable code!"}
            className="w-full h-56 bg-black/40 border border-white/10 rounded-xl p-4 text-sm font-mono text-gray-300 placeholder-gray-600 focus:outline-none focus:border-[var(--color-neon-blue)]/40 resize-none leading-relaxed"
            spellCheck={false}
          />
        )}

        {error && (
          <motion.div initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-3 bg-red-900/20 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400 text-sm">
            <AlertTriangle className="w-4 h-4 shrink-0" /> {error}
          </motion.div>
        )}

        <button
          onClick={handleScan}
          disabled={isScanning}
          className={`mt-5 w-full py-3.5 rounded-xl font-semibold text-white transition-all flex items-center justify-center gap-2 text-sm ${
            isScanning
              ? 'bg-white/5 border border-white/10 opacity-50 cursor-not-allowed'
              : 'bg-gradient-to-r from-[var(--color-neon-blue)]/20 to-[var(--color-neon-purple)]/20 border border-[var(--color-neon-blue)]/30 hover:border-[var(--color-neon-blue)]/60 hover:from-[var(--color-neon-blue)]/30 hover:to-[var(--color-neon-purple)]/30 cursor-pointer'
          }`}
        >
          {isScanning ? (
            <><Loader2 className="w-4 h-4 animate-spin" /> Running Autonomous Analysis...</>
          ) : (
            <><Activity className="w-4 h-4" /> Run Autonomous Scan</>
          )}
        </button>
      </motion.div>

      {/* ===== SCANNING ANIMATION ===== */}
      <AnimatePresence>
        {isScanning && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="glass-panel p-12 mb-8 flex flex-col items-center justify-center gap-4">
            <div className="relative">
              <Loader2 className="w-12 h-12 text-[var(--color-neon-blue)] animate-spin" />
              <div className="absolute inset-0 w-12 h-12 rounded-full animate-ping bg-[var(--color-neon-blue)]/10" />
            </div>
            <p className="text-lg text-white font-semibold">Autonomous Intelligence Engine Active</p>
            <div className="flex flex-col items-center gap-1 text-xs text-gray-400">
              <span>▸ Running Bandit static analysis...</span>
              <span>▸ Scanning for secrets & misconfigurations...</span>
              <span>▸ Correlating exploit chains...</span>
              <span>▸ Generating executive CISO report...</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ===== RESULTS ===== */}
      {ir && !isScanning && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>

          {/* Row 1: Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard title="Files Scanned" value={String(report.files_scanned || 1)}
              icon={<FileSearch className="w-5 h-5 text-[#00f0ff]" />}
              gradient="border-t-[var(--color-neon-blue)]" delay={0.1} />
            <StatCard title="Vulnerabilities" value={String(report.total_vulnerabilities || 0)}
              icon={<Crosshair className="w-5 h-5 text-[#ff8800]" />}
              gradient="border-t-[#ff8800]" delay={0.2} />
            <StatCard title="Exploit Chains" value={String(ir.exploit_chains?.length || 0)}
              icon={<GitBranch className="w-5 h-5 text-[#b026ff]" />}
              gradient="border-t-[var(--color-neon-purple)]" delay={0.3} />
            <StatCard title="Scan Time" value={`${report.scan_time_seconds}s`}
              icon={<Clock className="w-5 h-5 text-[#00ffcc]" />}
              gradient="border-t-[var(--color-neon-green)]" delay={0.4} />
          </div>

          {/* Row 2: Risk Gauge + Severity Chart + Executive Summary */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
            {/* Risk Gauge */}
            <div className="lg:col-span-3 glass-panel p-6 flex flex-col items-center justify-center">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Risk Assessment</h3>
              <RiskGauge score={ir.risk_score} level={ir.risk_level || "MEDIUM"} />
            </div>

            {/* Severity Distribution */}
            <div className="lg:col-span-3 glass-panel p-6">
              <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Severity Distribution</h3>
              {report.severity_stats && <SeverityChart stats={report.severity_stats} />}
            </div>

            {/* Executive Summary */}
            <div className="lg:col-span-6 glass-panel p-6 border-l-4 border-l-[var(--color-neon-red)] relative overflow-hidden">
              <div className="absolute top-2 right-2 opacity-5">
                <ShieldAlert className="w-24 h-24" />
              </div>
              <h3 className="text-xs font-semibold text-[#ff3366] uppercase tracking-wider mb-3 flex items-center gap-2">
                <ShieldAlert className="w-3.5 h-3.5" /> Virtual CISO — Executive Summary
              </h3>
              <p className="text-gray-300 text-sm leading-relaxed relative z-10 mb-4">
                {ir.executive_summary}
              </p>
              {ir.compliance_notes && (
                <div className="mt-3 pt-3 border-t border-white/10 relative z-10">
                  <p className="text-[11px] text-gray-500 leading-relaxed">
                    <span className="text-[var(--color-neon-blue)] font-semibold">COMPLIANCE: </span>
                    {ir.compliance_notes}
                  </p>
                </div>
              )}
              <div className="mt-4 pt-3 border-t border-white/10 relative z-10">
                <p className="text-[10px] text-gray-600 font-mono flex flex-col gap-0.5">
                  <span className="text-[var(--color-neon-green)] font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> TAMPER-EVIDENT AUDIT TRAIL
                  </span>
                  <span className="truncate" title={report.signature}>SHA-256: {report.signature}</span>
                  <span>TIMESTAMP: {report.timestamp}</span>
                </p>
              </div>
            </div>
          </div>

          {/* Row 3: Exploit Chains + Remediation */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <div className="lg:col-span-2 space-y-3">
              <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider flex items-center gap-2">
                <GitBranch className="w-4 h-4 text-[var(--color-neon-red)]" /> Exploit Chain Analysis
              </h2>
              <ExploitFlow chains={ir.exploit_chains} />
            </div>

            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider flex items-center gap-2">
                <Shield className="w-4 h-4 text-[var(--color-neon-blue)]" /> Remediation Priorities
              </h2>
              <div className="glass-panel p-5 space-y-3 max-h-[500px] overflow-y-auto">
                {ir.remediation_priorities?.map((p: any, i: number) => (
                  <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }}
                    className="flex gap-3 pb-3 border-b border-white/5 last:border-0 last:pb-0">
                    <span className={`shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold ${
                      i === 0 ? "bg-red-900/50 text-red-400 ring-1 ring-red-500/50" :
                      i === 1 ? "bg-orange-900/50 text-orange-400 ring-1 ring-orange-500/50" :
                      i === 2 ? "bg-yellow-900/50 text-yellow-400 ring-1 ring-yellow-500/50" :
                      "bg-gray-800/50 text-gray-400 ring-1 ring-gray-500/50"
                    }`}>{p.priority}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-white font-medium leading-snug">{p.action}</p>
                      {p.file && <p className="text-[10px] text-[var(--color-neon-blue)] font-mono mt-0.5">{p.file}</p>}
                      <p className="text-[10px] text-gray-500 mt-0.5">{p.reason?.substring(0, 100)}</p>
                      <div className="flex gap-2 mt-1">
                        <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                          p.severity === "CRITICAL" ? "bg-red-900/40 text-red-400" :
                          p.severity === "HIGH" ? "bg-orange-900/40 text-orange-400" :
                          "bg-yellow-900/40 text-yellow-400"
                        }`}>{p.severity}</span>
                        {p.effort && <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/5 text-gray-400">Effort: {p.effort}</span>}
                      </div>
                    </div>
                  </motion.div>
                ))}
                {(!ir.remediation_priorities || ir.remediation_priorities.length === 0) && (
                  <p className="text-xs text-gray-500 text-center py-4">No remediation required.</p>
                )}
              </div>
            </div>
          </div>

          {/* Row 4: Raw Findings Table (Collapsible) */}
          {report.raw_vulnerabilities?.length > 0 && (
            <div className="glass-panel">
              <button onClick={() => setShowRawFindings(!showRawFindings)}
                className="w-full p-5 flex items-center justify-between text-left cursor-pointer hover:bg-white/[0.02] transition-colors">
                <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-[var(--color-neon-blue)]" />
                  Detailed Scan Findings ({report.raw_vulnerabilities.length})
                </h2>
                {showRawFindings ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
              </button>

              <AnimatePresence>
                {showRawFindings && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden">
                    <div className="px-5 pb-5">
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-white/10 text-left">
                              <th className="pb-3 text-gray-500 font-medium text-[10px] uppercase tracking-wider">Severity</th>
                              <th className="pb-3 text-gray-500 font-medium text-[10px] uppercase tracking-wider">OWASP</th>
                              <th className="pb-3 text-gray-500 font-medium text-[10px] uppercase tracking-wider">Title</th>
                              <th className="pb-3 text-gray-500 font-medium text-[10px] uppercase tracking-wider">File</th>
                              <th className="pb-3 text-gray-500 font-medium text-[10px] uppercase tracking-wider">Line</th>
                              <th className="pb-3 text-gray-500 font-medium text-[10px] uppercase tracking-wider">Fix</th>
                            </tr>
                          </thead>
                          <tbody>
                            {report.raw_vulnerabilities.map((v: any, i: number) => (
                              <tr key={i} className="border-b border-white/5 hover:bg-white/[0.03] transition-colors">
                                <td className="py-2.5 pr-3">
                                  <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${
                                    v.severity === "CRITICAL" ? "bg-red-900/40 text-red-400" :
                                    v.severity === "HIGH" ? "bg-orange-900/40 text-orange-400" :
                                    v.severity === "MEDIUM" ? "bg-yellow-900/40 text-yellow-400" :
                                    "bg-blue-900/40 text-blue-400"
                                  }`}>{v.severity}</span>
                                </td>
                                <td className="py-2.5 pr-3">
                                  <span className="text-[10px] font-mono text-[var(--color-neon-purple)]">{v.owasp}</span>
                                </td>
                                <td className="py-2.5 pr-3 text-white text-xs font-medium max-w-[200px] truncate">{v.title || v.description}</td>
                                <td className="py-2.5 pr-3 font-mono text-[11px] text-[var(--color-neon-blue)] max-w-[150px] truncate">{v.file}</td>
                                <td className="py-2.5 pr-3 font-mono text-[11px] text-gray-400">{v.line}</td>
                                <td className="py-2.5 text-[11px] text-gray-500 max-w-[250px] truncate">{v.fix}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}
