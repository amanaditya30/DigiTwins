'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { 
  LayoutDashboard, 
  FileText, 
  Map, 
  Mic, 
  Code, 
  CheckSquare, 
  LogOut,
  Sparkles
} from 'lucide-react';
import { clearToken } from '@/utils/api';

export const Sidebar = () => {
  const pathname = usePathname();
  const router = useRouter();

  const menuItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Resume Auditor', href: '/resume', icon: FileText },
    { name: 'Roadmap & DSA', href: '/roadmap', icon: Map },
    { name: 'Mock Interview', href: '/interview', icon: Mic },
    { name: 'Project Auditor', href: '/projects', icon: Code },
    { name: 'Job Matcher', href: '/matcher', icon: CheckSquare },
  ];

  const handleLogout = () => {
    clearToken();
    router.push('/');
  };

  return (
    <aside className="w-64 bg-slate-950/80 backdrop-blur-md border-r border-white/5 flex flex-col h-screen fixed left-0 top-0 z-20">
      {/* Branding */}
      <div className="p-6 border-b border-white/5 flex items-center space-x-2">
        <Sparkles className="w-6 h-6 text-blue-400 animate-pulse" />
        <span className="text-xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
          Placement Twin
        </span>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-gradient-to-r from-blue-600/20 to-purple-600/20 text-blue-400 border-l-4 border-blue-500 shadow-md'
                  : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer logout */}
      <div className="p-4 border-t border-white/5">
        <button
          onClick={handleLogout}
          className="flex items-center space-x-3 w-full px-4 py-3 rounded-xl text-sm font-medium text-red-400 hover:bg-red-500/10 transition-all duration-200"
        >
          <LogOut className="w-4 h-4" />
          <span>Log Out</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
