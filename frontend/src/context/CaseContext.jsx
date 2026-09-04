import React, { createContext, useContext, useState, useEffect } from 'react';
import { caseAPI } from '../services/api';
import { useAuth } from './AuthContext';

const CaseContext = createContext(null);

export const CaseProvider = ({ children }) => {
  const { user } = useAuth();
  const [cases, setCases] = useState([]);
  const [currentCase, setCurrentCase] = useState(null);
  const [loading, setLoading] = useState(false);
  const [initialLoaded, setInitialLoaded] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchCases = async () => {
    if (!user) return;
    setLoading(true);
    try {
      const res = await caseAPI.getCases();
      let caseList = res.data.cases || [];

      // If database is clean/empty (e.g. fresh Render deployment), automatically seed demo case
      if (caseList.length === 0) {
        try {
          const demoRes = await caseAPI.seedDemoCase();
          if (demoRes?.data) {
            caseList = [demoRes.data];
          }
        } catch (seedErr) {
          console.warn('Auto-seed demo case failed:', seedErr);
        }
      }

      setCases(caseList);

      if (caseList.length > 0) {
        const savedId = Number(localStorage.getItem('forensics_selected_case_id'));
        const matched = caseList.find(c => c.id === savedId) ||
                        (currentCase && caseList.find(c => c.id === currentCase.id)) ||
                        caseList[0];
        setCurrentCase(matched);
        localStorage.setItem('forensics_selected_case_id', matched.id);
      } else {
        setCurrentCase(null);
      }
    } catch (err) {
      console.error('Failed to fetch cases:', err);
    } finally {
      setLoading(false);
      setInitialLoaded(true);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [user, refreshKey]);

  const selectCase = (caseId) => {
    const selected = cases.find(c => c.id === Number(caseId));
    if (selected) {
      setCurrentCase(selected);
      localStorage.setItem('forensics_selected_case_id', selected.id);
    }
  };

  const createNewCase = async (caseData) => {
    const res = await caseAPI.createCase(caseData);
    await fetchCases();
    setCurrentCase(res.data);
    if (res.data?.id) {
      localStorage.setItem('forensics_selected_case_id', res.data.id);
    }
    return res.data;
  };

  const loadDemoCase = async () => {
    const res = await caseAPI.seedDemoCase();
    await fetchCases();
    setCurrentCase(res.data);
    if (res.data?.id) {
      localStorage.setItem('forensics_selected_case_id', res.data.id);
    }
    return res.data;
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
      createNewCase,
      loadDemoCase,
      triggerRefresh,
      refreshKey,
      loading,
      initialLoaded
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
