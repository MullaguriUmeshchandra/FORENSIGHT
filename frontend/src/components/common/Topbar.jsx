import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useCase } from '../../context/CaseContext';
import { Menu, User as UserIcon, LogOut, ChevronDown, FolderOpen, RefreshCw } from 'lucide-react';

export const Topbar = ({ setMobileOpen }) => {
  const { user, logout } = useAuth();
  const { cases, currentCase, selectCase, triggerRefresh, loading } = useCase();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 bg-white border-b border-slate-200 shadow-sm md:px-8">
      {/* Left Area: Mobile Menu + Case Selector */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => setMobileOpen(true)}
          className="p-2 rounded-lg text-slate-600 hover:bg-slate-100 md:hidden"
          aria-label="Open navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Active Case Selector */}
        <div className="flex items-center space-x-2">
          <FolderOpen className="w-4 h-4 text-blue-600 shrink-0" />
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:inline">Active Case:</span>
          <select
            value={currentCase ? currentCase.id : ''}
            onChange={(e) => selectCase(e.target.value)}
            className="py-1.5 px-3 bg-slate-50 border border-slate-300 text-slate-800 text-xs rounded-lg font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all cursor-pointer max-w-[200px] sm:max-w-[280px]"
          >
            {cases.length === 0 ? (
              <option value="">No Cases Found</option>
            ) : (
              cases.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.case_number} — {c.case_name}
                </option>
              ))
            )}
          </select>
        </div>

        {/* Global Manual Sync Button */}
        <button
          onClick={triggerRefresh}
          disabled={loading}
          title="Refresh Case Metrics"
          className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-slate-100 rounded-md transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
        </button>
      </div>

      {/* Right Area: User Profile Dropdown */}
      <div className="relative">
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="flex items-center space-x-2.5 p-1.5 rounded-lg hover:bg-slate-100 transition-colors"
        >
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 text-white font-semibold text-xs shadow-sm">
            {user?.full_name ? user.full_name.charAt(0) : 'I'}
          </div>
          <div className="text-left hidden md:block">
            <span className="block text-xs font-bold text-slate-800 leading-tight">
              {user?.full_name || user?.username || 'Investigator'}
            </span>
            <span className="block text-[10px] text-blue-600 font-semibold uppercase tracking-wider">
              {user?.role || 'Investigator'}
            </span>
          </div>
          <ChevronDown className="w-4 h-4 text-slate-400" />
        </button>

        {/* Dropdown Menu */}
        {dropdownOpen && (
          <>
            <div
              className="fixed inset-0 z-40"
              onClick={() => setDropdownOpen(false)}
            />
            <div className="absolute right-0 z-50 w-56 mt-2 bg-white rounded-xl shadow-lg border border-slate-200 py-1 font-sans">
              <div className="px-4 py-2 border-b border-slate-100">
                <p className="text-xs font-semibold text-slate-800">{user?.full_name || 'Investigator'}</p>
                <p className="text-[11px] text-slate-400 truncate">{user?.email || 'investigator@forensics.local'}</p>
              </div>
              <button
                onClick={() => {
                  setDropdownOpen(false);
                  logout();
                }}
                className="flex items-center w-full px-4 py-2.5 text-xs text-red-600 hover:bg-red-50 font-medium transition-colors"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign Out
              </button>
            </div>
          </>
        )}
      </div>
    </header>
  );
};

export default Topbar;
