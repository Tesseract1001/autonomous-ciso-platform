"use client";

import { useState, useRef } from 'react';
import { 
  Activity, ShieldAlert, GitBranch, Crosshair, 
  Loader2, CheckCircle2, Upload, FileCode, AlertTriangle,
  ClipboardPaste, X
} from 'lucide-react';
import { StatCard } from './StatCard';
import { ExploitFlow } from './ExploitFlow';
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
          setError("Please paste some code to scan.");
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
      setError(e.message || "Failed to connect to the Intelligence Engine. Make sure the backend is running on port 8000.");
    } finally {
      setIsScanning(false);
    }
  };

  const ir = report?.intelligence_report;

  return (
    <div className="p-6 lg:p-8 max-w-[1400px] mx-auto">
      {/* Header */}
      <header className="mb-8 border-b border-white/10 pb-6 flex flex-col sm:flex-row justify-between sm:items-end gap-4">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold tracking-tight text-white mb-2">
            Autonomous <span className="text-glow-blue">Secure Software Intelligence</span>
          </h1>
          <p className="text-gray-400 text-sm">Virtual CISO Command Center — Real-time Exploit Chain Analysis</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[var(--color-neon-green)] animate-pulse" />
          <span className="text-xs font-mono text-[var(--color-neon-green)] uppercase">Engine Online</span>
        </div>
      </header>

      {/* Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard 
          title="Risk Score" 
          value={ir ? `${ir.risk_score} / 100` : "--"} 
          icon={<ShieldAlert className={`w-5 h-5 ${ir ? "text-[#ff3366]" : "text-gray-600"}`} />} 
          gradient={ir ? "border-t-[var(--color-neon-red)]" : "border-t-gray-800"}
          delay={0.1}
        />
        <StatCard 
          title="Exploit Chains" 
          value={ir?.exploit_chains ? String(ir.exploit_chains.length) : "--"} 
          icon={<GitBranch className={`w-5 h-5 ${ir ? "text-[#b026ff]" : "text-gray-600"}`} />} 
          gradient={ir ? "border-t-[var(--color-neon-purple)]" : "border-t-gray-800"}
          delay={0.2}
        />
        <StatCard 
          title="Scan Time" 
          value={report ? `${report.scan_time_seconds}s` : "--"} 
          icon={<Activity className={`w-5 h-5 ${report ? "text-[#00f0ff]" : "text-gray-600"}`} />} 
          gradient={report ? "border-t-[var(--color-neon-blue)]" : "border-t-gray-800"}
          delay={0.3}
        />
        <StatCard 
          title="Vulnerabilities" 
          value={report ? String(report.total_vulnerabilities) : "--"} 
          icon={<Crosshair className={`w-5 h-5 ${report ? "text-[#00f0ff]" : "text-gray-600"}`} />} 
          gradient={report ? "border-t-[var(--color-neon-blue)]" : "border-t-gray-800"}
          delay={0.4}
        />
      </div>

      {/* Upload / Paste Section */}
      <div className="glass-panel p-6 mb-8">
        <div className="flex items-center gap-4 mb-4">
          <button 
            onClick={() => setScanMode("upload")}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              scanMode === "upload" ? "bg-white/10 text-white border border-white/20" : "text-gray-500 hover:text-gray-300"
            }`}
          >
            <Upload className="w-4 h-4" /> Upload File / ZIP
          </button>
          <button 
            onClick={() => setScanMode("paste")}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              scanMode === "paste" ? "bg-white/10 text-white border border-white/20" : "text-gray-500 hover:text-gray-300"
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
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
              dragOver 
                ? "border-[var(--color-neon-blue)] bg-[var(--color-neon-blue)]/5" 
                : fileName 
                  ? "border-[var(--color-neon-green)]/50 bg-[var(--color-neon-green)]/5"
                  : "border-white/10 hover:border-white/30"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".py,.js,.ts,.zip,.jsx,.tsx,.java,.go,.php,.rb,.env,.yml,.yaml,.json"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleFileSelect(file);
              }}
            />
            {fileName ? (
              <div className="flex items-center justify-center gap-3">
                <FileCode className="w-8 h-8 text-[var(--color-neon-green)]" />
                <div>
                  <p className="text-white font-semibold">{fileName}</p>
                  <p className="text-xs text-gray-400">Click scan to analyze</p>
                </div>
                <button onClick={(e) => { e.stopPropagation(); setFileName(null); selectedFileRef.current = null; }}>
                  <X className="w-4 h-4 text-gray-500 hover:text-white" />
                </button>
              </div>
            ) : (
              <div>
                <Upload className="w-10 h-10 mx-auto text-gray-500 mb-3" />
                <p className="text-gray-300 font-medium">Drop your source code or ZIP file here</p>
                <p className="text-xs text-gray-500 mt-1">Supports .py, .js, .ts, .java, .go, .zip and more</p>
              </div>
            )}
          </div>
        ) : (
          <textarea
            value={pastedCode}
            onChange={(e) => setPastedCode(e.target.value)}
            placeholder="Paste your source code here..."
            className="w-full h-48 bg-black/30 border border-white/10 rounded-xl p-4 text-sm font-mono text-gray-300 placeholder-gray-600 focus:outline-none focus:border-[var(--color-neon-blue)]/50 resize-none"
          />
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-900/20 border border-red-500/30 rounded-lg flex items-center gap-2 text-red-400 text-sm">
            <AlertTriangle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        <button 
          onClick={handleScan}
          disabled={isScanning}
          className={`mt-4 w-full glass-panel py-3 font-semibold text-white transition-all flex items-center justify-center gap-2
            ${isScanning ? 'opacity-50 cursor-not-allowed' : 'hover:bg-white/5 border-glow cursor-pointer'}
          `}
        >
          {isScanning ? (
            <><Loader2 className="w-4 h-4 animate-spin text-[var(--color-neon-blue)]" /> Scanning & Analyzing...</>
          ) : (
            <><Activity className="w-4 h-4 text-[var(--color-neon-blue)]" /> Run Autonomous Scan</>
          )}
        </button>
      </div>

      {/* Results: Exploit Chains + Executive Summary */}
      {(ir || isScanning) && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-[var(--color-neon-blue)]" />
              Exploit Chain Visualizer
            </h2>
            {isScanning ? (
              <div className="glass-panel h-[450px] flex flex-col items-center justify-center gap-4">
                <Loader2 className="w-8 h-8 text-[var(--color-neon-blue)] animate-spin" />
                <p className="text-sm text-gray-400 animate-pulse">Building exploit chain graph...</p>
              </div>
            ) : (
              <ExploitFlow chains={ir?.exploit_chains} />
            )}
          </div>

          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white border-b border-white/10 pb-2">
              Virtual CISO Report
            </h2>
            
            <AnimatePresence mode="wait">
              {isScanning && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  className="glass-panel p-6 border-l-4 border-l-[var(--color-neon-blue)] flex flex-col items-center justify-center gap-4 py-12"
                >
                  <Loader2 className="w-8 h-8 text-[var(--color-neon-blue)] animate-spin" />
                  <p className="text-sm text-[var(--color-neon-blue)] animate-pulse text-center">AI reasoning engine analyzing vulnerabilities...</p>
                </motion.div>
              )}

              {ir && !isScanning && (
                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
                  className="glass-panel p-5 border-l-4 border-l-[var(--color-neon-red)] relative overflow-hidden"
                >
                  <div className="absolute top-0 right-0 p-2 opacity-5">
                    <ShieldAlert className="w-20 h-20" />
                  </div>
                  
                  <h3 className="text-base font-bold text-[#ff3366] mb-3 uppercase tracking-wider text-glow-red flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4" /> Executive Summary
                  </h3>
                  <p className="text-gray-300 text-sm leading-relaxed mb-4 relative z-10">
                    {ir.executive_summary}
                  </p>

                  {ir.remediation_priorities?.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-white/10 relative z-10">
                      <h4 className="text-xs font-bold text-[var(--color-neon-blue)] uppercase tracking-wider mb-2">Remediation Priorities</h4>
                      <ol className="space-y-2">
                        {ir.remediation_priorities.map((p: any, i: number) => (
                          <li key={i} className="text-xs text-gray-400 flex gap-2">
                            <span className={`shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${
                              i === 0 ? "bg-red-900/50 text-red-400" : i === 1 ? "bg-orange-900/50 text-orange-400" : "bg-yellow-900/50 text-yellow-400"
                            }`}>{p.priority}</span>
                            <span>{p.action}</span>
                          </li>
                        ))}
                      </ol>
                    </div>
                  )}

                  <div className="mt-4 pt-3 border-t border-white/10 relative z-10">
                    <p className="text-xs text-gray-500 font-mono flex flex-col gap-1">
                      <span className="text-[var(--color-neon-green)] font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> CRYPTOGRAPHIC AUDIT TRAIL
                      </span>
                      <span className="truncate w-full text-[10px]" title={report.signature}>
                        SHA-256: {report.signature}
                      </span>
                      <span className="text-[10px]">TIMESTAMP: {report.timestamp}</span>
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Raw Vulnerabilities Table */}
      {report?.raw_vulnerabilities?.length > 0 && (
        <div className="glass-panel p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-[var(--color-neon-blue)]" />
            Raw Scan Results ({report.raw_vulnerabilities.length} findings)
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10 text-left">
                  <th className="pb-3 text-gray-400 font-medium text-xs uppercase">Severity</th>
                  <th className="pb-3 text-gray-400 font-medium text-xs uppercase">Rule</th>
                  <th className="pb-3 text-gray-400 font-medium text-xs uppercase">Description</th>
                  <th className="pb-3 text-gray-400 font-medium text-xs uppercase">File</th>
                  <th className="pb-3 text-gray-400 font-medium text-xs uppercase">Line</th>
                </tr>
              </thead>
              <tbody>
                {report.raw_vulnerabilities.map((v: any, i: number) => (
                  <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 pr-4">
                      <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${
                        v.severity === "CRITICAL" ? "bg-red-900/40 text-red-400" :
                        v.severity === "HIGH" ? "bg-orange-900/40 text-orange-400" :
                        v.severity === "MEDIUM" ? "bg-yellow-900/40 text-yellow-400" :
                        "bg-blue-900/40 text-blue-400"
                      }`}>
                        {v.severity}
                      </span>
                    </td>
                    <td className="py-3 pr-4 font-mono text-xs text-gray-400">{v.rule_id}</td>
                    <td className="py-3 pr-4 text-gray-300 text-xs max-w-xs truncate">{v.description}</td>
                    <td className="py-3 pr-4 font-mono text-xs text-[var(--color-neon-blue)]">{v.file}</td>
                    <td className="py-3 font-mono text-xs text-gray-400">{v.line}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
