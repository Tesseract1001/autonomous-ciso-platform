"use client";

import { motion } from "framer-motion";

export function StatCard({ title, value, icon, gradient, delay = 0 }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className={`glass-panel p-6 border-t-2 ${gradient}`}
    >
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-gray-400 text-sm font-semibold tracking-wider uppercase mb-2">{title}</h3>
          <div className="text-3xl font-bold text-white">{value}</div>
        </div>
        <div className="p-3 bg-white/5 rounded-lg border border-white/10">
          {icon}
        </div>
      </div>
    </motion.div>
  );
}
