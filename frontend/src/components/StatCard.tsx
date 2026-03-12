"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: React.ReactNode;
  gradient: string;
  delay?: number;
}

export function StatCard({ title, value, subtitle, icon, gradient, delay = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={`glass-panel p-5 border-t-2 ${gradient} hover:scale-[1.02] transition-transform`}
    >
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-gray-400 text-[11px] font-semibold tracking-wider uppercase mb-1">{title}</h3>
          <div className="text-2xl font-bold text-white font-[var(--font-space)]">{value}</div>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <div className="p-2.5 bg-white/5 rounded-lg border border-white/10">
          {icon}
        </div>
      </div>
    </motion.div>
  );
}
