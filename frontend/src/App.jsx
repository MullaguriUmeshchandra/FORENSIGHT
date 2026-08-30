import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { CaseProvider } from './context/CaseContext';

import Sidebar from './components/common/Sidebar';
import Topbar from './components/common/Topbar';

import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import EvidencePage from './pages/EvidencePage';
import TimelinePage from './pages/TimelinePage';
import GapsPage from './pages/GapsPage';
import RecommendationsPage from './pages/RecommendationsPage';
import InvestigationPage from './pages/InvestigationPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';

// Protected App Layout Component
const ProtectedLayout = ({ children }) => {
  const { user, loading } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-900 text-white text-xs font-semibold">
        Verifying forensics authorization...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <CaseProvider>
      <div className="flex min-h-screen bg-slate-50 font-sans">
        {/* Sidebar */}
        <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col md:pl-64 min-w-0">
          <Topbar setMobileOpen={setMobileOpen} />

          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
            {children}
          </main>
        </div>
      </div>
    </CaseProvider>
  );
};

export function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route path="/dashboard" element={<ProtectedLayout><DashboardPage /></ProtectedLayout>} />
          <Route path="/evidence" element={<ProtectedLayout><EvidencePage /></ProtectedLayout>} />
          <Route path="/timeline" element={<ProtectedLayout><TimelinePage /></ProtectedLayout>} />
          <Route path="/gaps" element={<ProtectedLayout><GapsPage /></ProtectedLayout>} />
          <Route path="/recommendations" element={<ProtectedLayout><RecommendationsPage /></ProtectedLayout>} />
          <Route path="/investigation" element={<ProtectedLayout><InvestigationPage /></ProtectedLayout>} />
          <Route path="/reports" element={<ProtectedLayout><ReportsPage /></ProtectedLayout>} />
          <Route path="/settings" element={<ProtectedLayout><SettingsPage /></ProtectedLayout>} />

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
