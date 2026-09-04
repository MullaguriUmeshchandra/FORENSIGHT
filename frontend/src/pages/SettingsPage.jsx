import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { systemAPI } from '../services/api';
import StatusBadge from '../components/common/StatusBadge';
import { User, Shield, Server, Sliders, Database, HardDrive, CheckCircle } from 'lucide-react';

export const SettingsPage = () => {
  const { user } = useAuth();
  const [health, setHealth] = useState(null);

  useEffect(() => {
    systemAPI.getHealth()
      .then(res => setHealth(res.data))
      .catch(() => setHealth({ status: 'offline', database: 'error', neo4j: 'offline' }));
  }, []);

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          System Settings & User Profile
        </h1>
        <p className="text-xs text-slate-500 font-medium mt-1">
          Review investigator credentials, role permissions, forensic analysis thresholds, and system health.
        </p>
      </div>

      {/* Profile Card */}
      <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center">
          <User className="w-4 h-4 text-blue-600 mr-2" />
          Investigator Account Profile
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <span className="text-[10px] font-semibold text-slate-400 block">Full Name</span>
            <span className="font-bold text-slate-800">{user?.full_name || 'N/A'}</span>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <span className="text-[10px] font-semibold text-slate-400 block">Username</span>
            <span className="font-mono font-bold text-slate-800">{user?.username}</span>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <span className="text-[10px] font-semibold text-slate-400 block">Email Address</span>
            <span className="font-semibold text-slate-800">{user?.email}</span>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <span className="text-[10px] font-semibold text-slate-400 block">Assigned Role</span>
            <div className="mt-1"><StatusBadge status={user?.role} /></div>
          </div>
        </div>
      </div>

      {/* Forensic Threshold Preferences */}
      <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center">
          <Sliders className="w-4 h-4 text-blue-600 mr-2" />
          Forensic Gap Calculation Thresholds
        </h3>

        <div className="space-y-3 text-xs">
          <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <div>
              <span className="font-bold text-slate-800 block">Ignored Interval</span>
              <span className="text-[11px] text-slate-500">Deltas under 2 minutes are treated as standard operational pacing.</span>
            </div>
            <span className="font-mono font-bold text-slate-600">&lt; 120 seconds</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <div>
              <span className="font-bold text-slate-800 block">Low Severity Gap</span>
              <span className="text-[11px] text-slate-500">Deltas between 2 minutes and 5 minutes.</span>
            </div>
            <span className="font-mono font-bold text-emerald-600">120s – 300s</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <div>
              <span className="font-bold text-slate-800 block">Medium Severity Gap</span>
              <span className="text-[11px] text-slate-500">Deltas between 5 minutes and 15 minutes.</span>
            </div>
            <span className="font-mono font-bold text-amber-600">300s – 900s</span>
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <div>
              <span className="font-bold text-slate-800 block">High Severity Gap</span>
              <span className="text-[11px] text-slate-500">Deltas exceeding 15 minutes.</span>
            </div>
            <span className="font-mono font-bold text-red-600">&gt; 900 seconds</span>
          </div>
        </div>
      </div>

      {/* System Health */}
      <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="text-sm font-bold text-slate-900 flex items-center">
          <Server className="w-4 h-4 text-blue-600 mr-2" />
          Backend Connection & Infrastructure Telemetry
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <span className="text-[10px] font-semibold text-slate-400 block">FastAPI Service</span>
            <span className="font-bold text-emerald-600 flex items-center mt-1">
              <CheckCircle className="w-3.5 h-3.5 mr-1" />
              {health?.service || 'Active'}
            </span>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <span className="text-[10px] font-semibold text-slate-400 block">Relational Database</span>
            <span className="font-bold text-emerald-600 flex items-center mt-1">
              <Database className="w-3.5 h-3.5 mr-1" />
              {health?.database || 'Connected'}
            </span>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
            <span className="text-[10px] font-semibold text-slate-400 block">Neo4j Graph Database</span>
            <span className="font-bold text-blue-600 flex items-center mt-1">
              <HardDrive className="w-3.5 h-3.5 mr-1" />
              {health?.neo4j || 'Active'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
