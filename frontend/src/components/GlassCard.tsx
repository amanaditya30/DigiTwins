import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
}

export const GlassCard: React.FC<GlassCardProps> = ({ children, className = '' }) => {
  return (
    <div className={`bg-slate-900/40 backdrop-blur-xl border border-white/5 rounded-2xl p-6 shadow-xl hover:border-white/10 transition-all duration-300 ${className}`}>
      {children}
    </div>
  );
};

export default GlassCard;
