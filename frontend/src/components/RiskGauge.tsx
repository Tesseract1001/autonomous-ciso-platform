"use client";

import { motion } from "framer-motion";

interface RiskGaugeProps {
  score: number;
  level: string;
}

export function RiskGauge({ score, level }: RiskGaugeProps) {
  const circumference = 2 * Math.PI * 54;
  const progress = (score / 100) * circumference;
  const remaining = circumference - progress;

  const getColor = () => {
    if (score >= 80) return { stroke: "#ff3366", glow: "rgba(255,51,102,0.4)", text: "#ff3366" };
    if (score >= 60) return { stroke: "#ff8800", glow: "rgba(255,136,0,0.4)", text: "#ff8800" };
    if (score >= 40) return { stroke: "#ffcc00", glow: "rgba(255,204,0,0.3)", text: "#ffcc00" };
    return { stroke: "#00ffcc", glow: "rgba(0,255,204,0.3)", text: "#00ffcc" };
  };

  const colors = getColor();

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-36 h-36">
        <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
          {/* Background ring */}
          <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
          {/* Progress ring */}
          <motion.circle
            cx="60" cy="60" r="54" fill="none"
            stroke={colors.stroke}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: remaining }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            style={{ filter: `drop-shadow(0 0 8px ${colors.glow})` }}
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-3xl font-bold font-[var(--font-space)]"
            style={{ color: colors.text }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {score}
          </motion.span>
          <span className="text-[10px] text-gray-400 uppercase tracking-widest">/ 100</span>
        </div>
      </div>
      <motion.span
        className="mt-2 text-xs font-bold uppercase tracking-widest px-3 py-1 rounded-full"
        style={{ color: colors.text, backgroundColor: `${colors.stroke}15`, border: `1px solid ${colors.stroke}30` }}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
      >
        {level} RISK
      </motion.span>
    </div>
  );
}
