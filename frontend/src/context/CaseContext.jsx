import React, { createContext, useContext, useState, useEffect } from 'react';
import { caseAPI } from '../services/api';
import { useAuth } from './AuthContext';

const CaseContext = createContext(null);

export const CaseProvider = ({ children }) => {
  const { user } = useAuth();
  const [cases, setCases] = useState([]);
  const [currentCase, setCurrentCase] = useState(null);
  const [loading, setLoading] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchCases = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const res = await caseAPI.getCases();
      const caseList = res.data.cases || [];
      setCases(caseList);

      // Auto-select first case (e.g. CASE-001) if not selected or current no longer valid
      if (caseList.length > 0) {
        if (!currentCase || !caseList.find(c => c.id === currentCase.id)) {
          setCurrentCase(caseList[0]);
        } else {
          // Update currentCase stats
          const updated = caseList.find(c => c.id === currentCase.id);
          setCurrentCase(updated);
        }
      }
    } catch (err) {
      console.error('Failed to fetch cases:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [user, refreshKey]);

  const selectCase = (caseId) => {
    const selected = cases.find(c => c.id === Number(caseId));
    if (selected) {
      setCurrentCase(selected);
    }
  };

  const triggerRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <CaseContext.Provider value={{
      cases,
      currentCase,
      setCurrentCase,
      selectCase,
      fetchCases,
      triggerRefresh,
      refreshKey,
      loading
    }}>
      {children}
    </CaseContext.Provider>
  );
};

export const useCase = () => {
  const context = useContext(CaseContext);
  if (!context) {
    throw new Error('useCase must be used within a CaseProvider');
  }
  return context;
};
