import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useCase } from '../../context/CaseContext';
import Modal from './Modal';
import { Menu, User as UserIcon, LogOut, ChevronDown, FolderOpen, RefreshCw, Plus, Sparkles, FolderPlus } from 'lucide-react';

export const Topbar = ({ setMobileOpen }) => {
  const { user, logout, isInvestigator } = useAuth();
  const { cases, currentCase, selectCase, triggerRefresh, loading, createNewCase, loadDemoCase } = useCase();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [caseNumber, setCaseNumber] = useState('');
  const [caseName, setCaseName] = useState('');
  const [description, setDescription] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleCreateCase = async (e) => {
    e.preventDefault();
    if (!caseNumber.trim() || !caseName.trim()) {
      setErrorMsg('Case number and name are required.');
      return;
    }
    setActionLoading(true);
    setErrorMsg('');
    try {
      await createNewCase({
        case_number: caseNumber.trim(),
        case_name: caseName.trim(),
        description: description.trim() || undefined
      });
      setModalOpen(false);
      setCaseNumber('');
      setCaseName('');
      setDescription('');
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to create case.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleLoadDemo = async () => {
    setActionLoading(true);
    setErrorMsg('');
    try {
      await loadDemoCase();
      setModalOpen(false);
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to seed demo case.');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <>
      <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 bg-white border-b border-slate-200 shadow-sm md:px-8">
        {/* Left Area: Mobile Menu + Case Selector + Add Case */}
        <div className="flex items-center space-x-3 sm:space-x-4">
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
              className="py-1.5 px-3 bg-slate-50 border border-slate-300 text-slate-800 text-xs rounded-lg font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all cursor-pointer max-w-[180px] sm:max-w-[260px]"
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

          {/* Add New Case Button */}
          {isInvestigator && (
            <button
              onClick={() => setModalOpen(true)}
              className="inline-flex items-center px-2.5 py-1.5 text-xs font-bold text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors shadow-xs"
              title="Create New Forensic Case"
            >
              <Plus className="w-3.5 h-3.5 sm:mr-1" />
              <span className="hidden sm:inline">New Case</span>
            </button>
          )}

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

      {/* New Case Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Create Forensic Investigation Case"
      >
        <form onSubmit={handleCreateCase} className="space-y-4">
          {errorMsg && (
            <div className="p-3 text-xs text-red-700 bg-red-50 border border-red-200 rounded-lg">
              {errorMsg}
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Case Number / Identifier *</label>
            <input
              type="text"
              required
              placeholder="e.g. CASE-2026-002"
              value={caseNumber}
              onChange={(e) => setCaseNumber(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Case Title / Incident Name *</label>
            <input
              type="text"
              required
              placeholder="e.g. Internal Server Unauthorized Access Analysis"
              value={caseName}
              onChange={(e) => setCaseName(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Description / Scope</label>
            <textarea
              rows={3}
              placeholder="Provide context, affected endpoints, and forensic hypothesis..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-slate-200">
            <button
              type="button"
              onClick={handleLoadDemo}
              disabled={actionLoading}
              className="inline-flex items-center text-xs font-semibold text-purple-700 hover:text-purple-900"
            >
              <Sparkles className="w-3.5 h-3.5 mr-1 text-purple-600" />
              Load Pre-built CASE-001 Scenario
            </button>

            <div className="flex space-x-2">
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={actionLoading}
                className="px-4 py-1.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm disabled:opacity-50"
              >
                {actionLoading ? 'Creating...' : 'Create Case'}
              </button>
            </div>
          </div>
        </form>
      </Modal>
    </>
  );
};

export default Topbar;
