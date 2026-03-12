"use client";

import { motion } from "framer-motion";

interface SeverityChartProps {
  stats: { CRITICAL: number; HIGH: number; MEDIUM: number; LOW: number; INFO: number };
}

const SEVERITY_COLORS: Record<string, { color: string; label: string }> = {
  CRITICAL: { color: "#ff3366", label: "Critical" },
  HIGH: { color: "#ff8800", label: "High" },
  MEDIUM: { color: "#ffcc00", label: "Medium" },
  LOW: { color: "#00f0ff", label: "Low" },
  INFO: { color: "#666666", label: "Info" },
};

export function SeverityChart({ stats }: SeverityChartProps) {
  const total = Object.values(stats).reduce((a, b) => a + b, 0);
  if (total === 0) return null;

  // Build SVG donut segments
  const segments: { key: string; value: number; color: string; offset: number }[] = [];
  let offset = 0;
  const circumference = 2 * Math.PI * 40;

  for (const [key, value] of Object.entries(stats)) {
    if (value === 0) continue;
    segments.push({ key, value, color: SEVERITY_COLORS[key]?.color || "#666", offset });
    offset += (value / total) * circumference;
  }

  return (
    <div className="flex items-center gap-6">
      <div className="relative w-28 h-28 shrink-0">
        <svg viewBox="0 0 100 100" className="w-full h-full -rotate-90">
          {segments.map((seg, i) => {
            const dashLength = (seg.value / total) * circumference;
            const gapLength = circumference - dashLength;
            return (
              <motion.circle
                key={seg.key}
                cx="50" cy="50" r="40" fill="none"
                stroke={seg.color}
                strokeWidth="10"
                strokeDasharray={`${dashLength} ${gapLength}`}
                strokeDashoffset={-seg.offset}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: i * 0.1 + 0.3 }}
              />
            );
          })}
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-bold text-white">{total}</span>
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        {Object.entries(stats).map(([key, value]) => {
          if (value === 0) return null;
          const meta = SEVERITY_COLORS[key];
          return (
            <div key={key} className="flex items-center gap-2 text-xs">
              <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: meta?.color }} />
              <span className="text-gray-400 w-14">{meta?.label}</span>
              <span className="text-white font-semibold">{value}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
