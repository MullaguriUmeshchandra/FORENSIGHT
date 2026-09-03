import React, { useState } from 'react';
import { useCase } from '../../context/CaseContext';
import { caseAPI } from '../../services/api';
import Modal from './Modal';
import { FolderPlus, AlertCircle, RefreshCw } from 'lucide-react';

export const CreateCaseModal = ({ isOpen, onClose }) => {
  const { fetchCases, setCurrentCase } = useCase();
  const [caseNumber, setCaseNumber] = useState('');
  const [caseName, setCaseName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!caseNumber.trim() || !caseName.trim()) {
      setError('Case Number and Case Name are required.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await caseAPI.createCase({
        case_number: caseNumber.trim().toUpperCase(),
        case_name: caseName.trim(),
        description: description.trim() || undefined,
        status: 'OPEN',
      });

      const newCase = res.data;
      await fetchCases();
      setCurrentCase(newCase);
      
      // Reset form & close
      setCaseNumber('');
      setCaseName('');
      setDescription('');
      onClose();
    } catch (err) {
      console.error('Failed to create case:', err);
      setError(err.response?.data?.detail || 'Failed to create case.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Forensic Case">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-center">
            <AlertCircle className="w-4 h-4 mr-2 shrink-0 text-red-500" />
            <span>{error}</span>
          </div>
        )}

        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
            Case Number / ID *
          </label>
          <input
            type="text"
            required
            placeholder="e.g. CASE-2026-002"
            value={caseNumber}
            onChange={(e) => setCaseNumber(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-xs font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none uppercase font-mono"
          />
          <p className="text-[11px] text-slate-400 mt-1">Unique forensic case identifier.</p>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
            Case Title / Incident Name *
          </label>
          <input
            type="text"
            required
            placeholder="e.g. Financial Exfiltration & Account Takeover"
            value={caseName}
            onChange={(e) => setCaseName(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-xs font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
            Investigation Description
          </label>
          <textarea
            rows="3"
            placeholder="Summary of incident scope, target hosts, and forensic hypothesis..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-xs text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        <div className="flex items-center justify-end space-x-3 pt-2 border-t border-slate-100">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg shadow-sm transition-colors disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                Creating Case...
              </>
            ) : (
              <>
                <FolderPlus className="w-3.5 h-3.5 mr-1.5" />
                Create Case
              </>
            )}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default CreateCaseModal;
