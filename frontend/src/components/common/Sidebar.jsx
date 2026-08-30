import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderArchive,
  Clock,
  AlertTriangle,
  Lightbulb,
  Network,
  FileText,
  Settings,
  HelpCircle,
  Shield,
  X
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Evidence', path: '/evidence', icon: FolderArchive },
  { name: 'Timeline', path: '/timeline', icon: Clock },
  { name: 'Gap Detection', path: '/gaps', icon: AlertTriangle },
  { name: 'Recommendations', path: '/recommendations', icon: Lightbulb },
  { name: 'Investigation', path: '/investigation', icon: Network },
  { name: 'Reports', path: '/reports', icon: FileText },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const Sidebar = ({ mobileOpen, setMobileOpen }) => {
  return (
    <>
      {/* Mobile Backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-sm md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col w-64 bg-slate-900 text-slate-300 transition-transform duration-300 ease-in-out md:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-slate-800">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-blue-600 text-white font-bold shadow-md shadow-blue-600/30">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <span className="text-base font-bold text-white tracking-wide">Forensics Hub</span>
              <span className="block text-[10px] text-slate-400 font-mono font-medium uppercase tracking-wider">v1.0 Reconstruction</span>
            </div>
          </div>
          <button
            className="p-1 rounded-md text-slate-400 hover:text-white md:hidden"
            onClick={() => setMobileOpen(false)}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `flex items-center px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/40'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                  }`
                }
              >
                <Icon className="w-5 h-5 mr-3 shrink-0" />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom Help Widget (Matching Reference Image 2) */}
        <div className="p-4 m-4 rounded-xl bg-slate-800/80 border border-slate-700/60">
          <div className="flex items-center space-x-2 text-blue-400 mb-1">
            <HelpCircle className="w-5 h-5 shrink-0" />
            <span className="text-sm font-semibold text-white">Need Help?</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed mb-3">
            Learn how to get the most out of the system.
          </p>
          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="block w-full py-2 text-center text-xs font-semibold text-white bg-slate-700/80 hover:bg-slate-700 rounded-lg border border-slate-600 transition-colors"
          >
            View Guide
          </a>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
