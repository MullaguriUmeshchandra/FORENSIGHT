import React, { useState, useEffect, useRef } from 'react';
import { useCase } from '../context/CaseContext';
import { evidenceAPI, timelineAPI } from '../services/api';
import StatusBadge from '../components/common/StatusBadge';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';
import CreateCaseModal from '../components/common/CreateCaseModal';
import { 
  Upload, FileUp, CheckCircle, AlertCircle, HardDrive, RefreshCw, 
  Trash2, FileText, FolderPlus, Download, Sparkles, AlertTriangle 
} from 'lucide-react';

const SAMPLE_TEMPLATES = {
  system_logs: {
    filename: 'sample_system_logs.csv',
    device: 'WORKSTATION-01',
    source_type: 'SYSTEM_LOGS',
    label: 'Windows Security Logs (.csv)',
    desc: 'Interactive logon, privilege escalation, and audit log clearing (Event 1102).',
    content: `timestamp,event_type,device,event_description,source_ip,user_id
2026-08-30T10:00:15Z,USER_LOGON,WORKSTATION-01,User jdoe interactive logon successful (LogonType: 2, Domain: CORP),192.168.1.105,jdoe
2026-08-30T10:05:22Z,PRIVILEGE_ELEVATION,WORKSTATION-01,Special privileges assigned to new logon session (SeDebugPrivilege, SeTcbPrivilege),192.168.1.105,jdoe
2026-08-30T10:12:40Z,PROCESS_CREATION,WORKSTATION-01,Process powershell.exe created with PID 4120 by explorer.exe (Parent PID 1240),192.168.1.105,jdoe
2026-08-30T10:18:05Z,REGISTRY_MODIFICATION,WORKSTATION-01,HKLM\\System\\CurrentControlSet\\Services\\AuditLog modified to disable security tracking,192.168.1.105,SYSTEM
2026-08-30T10:28:10Z,AUDIT_LOG_CLEARED,WORKSTATION-01,The security event log was intentionally cleared by user administrator (Event ID 1102),192.168.1.105,jdoe
2026-08-30T10:41:30Z,SERVICE_STARTED,WORKSTATION-01,Service 'SysMain' entered the running state,192.168.1.105,SYSTEM
2026-08-30T10:45:12Z,USER_LOGOFF,WORKSTATION-01,User jdoe initiated session termination and logoff,192.168.1.105,jdoe`
  },
  browser_history: {
    filename: 'sample_browser_history.json',
    device: 'WORKSTATION-01',
    source_type: 'BROWSER_ARTIFACTS',
    label: 'Browser Artifacts (.json)',
    desc: 'Google search for wiping tools, Mega upload portal visit, and cache purge.',
    content: JSON.stringify([
      {
        "timestamp": "2026-08-30T10:02:10Z",
        "event_type": "BROWSER_SEARCH",
        "event_description": "Search query: 'how to delete event viewer logs permanently without trace'",
        "device": "WORKSTATION-01",
        "url": "https://www.google.com/search?q=how+to+delete+event+viewer+logs",
        "browser": "Chrome/128.0"
      },
      {
        "timestamp": "2026-08-30T10:08:45Z",
        "event_type": "BROWSER_NAVIGATION",
        "event_description": "Visited file upload portal https://mega.nz/upload for cloud storage",
        "device": "WORKSTATION-01",
        "url": "https://mega.nz/upload",
        "browser": "Chrome/128.0"
      },
      {
        "timestamp": "2026-08-30T10:14:18Z",
        "event_type": "BROWSER_DOWNLOAD",
        "event_description": "Downloaded tool 'sdelete64.exe' from Sysinternals repository",
        "device": "WORKSTATION-01",
        "url": "https://download.sysinternals.com/files/SDelete.zip",
        "browser": "Chrome/128.0"
      },
      {
        "timestamp": "2026-08-30T10:22:04Z",
        "event_type": "CLOUD_FILE_UPLOAD",
        "event_description": "Encrypted archive 'Q3_Financial_Projections_Confidential.7z' uploaded to MegaCloud (45.2 MB)",
        "device": "WORKSTATION-01",
        "url": "https://mega.nz/file/transfer_complete",
        "browser": "Chrome/128.0"
      },
      {
        "timestamp": "2026-08-30T10:43:50Z",
        "event_type": "BROWSER_CLEARED",
        "event_description": "Browser cache, cookies, and history cleared by user command",
        "device": "WORKSTATION-01",
        "url": "chrome://settings/clearBrowserData",
        "browser": "Chrome/128.0"
      }
    ], null, 2)
  },
  usb_logs: {
    filename: 'sample_usb_logs.csv',
    device: 'WORKSTATION-01',
    source_type: 'USB_LOGS',
    label: 'USB & Removable Storage (.csv)',
    desc: 'SanDisk mass storage insertion, sensitive financial spreadsheet copy, and removal.',
    content: `timestamp,event_type,device,event_description,vendor_id,serial_number,volume_label
2026-08-30T10:10:02Z,USB_DEVICE_INSERTED,WORKSTATION-01,SanDisk Ultra USB 3.0 mass storage device connected,0781,4C531001560719115254,BACKUP_DRIVE
2026-08-30T10:11:15Z,FILE_COPY_TO_REMOVABLE,WORKSTATION-01,Copied 348 internal financial database spreadsheets to E:\\Sensitive_Ledgers\\,0781,4C531001560719115254,BACKUP_DRIVE
2026-08-30T10:25:40Z,USB_DEVICE_REMOVED,WORKSTATION-01,SanDisk Ultra USB 3.0 safely disconnected and unmounted,0781,4C531001560719115254,BACKUP_DRIVE`
  },
  auth_syslog: {
    filename: 'sample_auth_syslog.log',
    device: 'DC-SRV-01',
    source_type: 'SYSTEM_LOGS',
    label: 'Authentication Syslog (.log)',
    desc: 'SSH public key login on domain controller and sudo privilege elevation.',
    content: `Aug 30 10:00:15 dc-srv-01 sshd[28410]: Accepted publickey for jdoe from 192.168.1.105 port 52314 ssh2
Aug 30 10:04:12 dc-srv-01 sudo: jdoe : TTY=pts/2 ; PWD=/home/jdoe ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow
Aug 30 10:19:33 dc-srv-01 sshd[29104]: Connection closed by 192.168.1.105 port 52314 [preauth]
Aug 30 10:44:50 dc-srv-01 session-manager: pam_unix(sshd:session): session closed for user jdoe`
  }
};

export const EvidencePage = () => {
  const { currentCase, triggerRefresh } = useCase();
  const [evidenceList, setEvidenceList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const [createCaseModalOpen, setCreateCaseModalOpen] = useState(false);

  // Form State
  const [selectedFile, setSelectedFile] = useState(null);
  const [deviceName, setDeviceName] = useState('WORKSTATION-01');
  const [sourceType, setSourceType] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const fetchEvidence = async () => {
    if (!currentCase) {
      setLoading(false);
      setEvidenceList([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await evidenceAPI.getEvidence(currentCase.id);
      setEvidenceList(res.data.evidence || []);
    } catch (err) {
      console.error('Failed to load evidence:', err);
      setError('Unable to load evidence inventory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, [currentCase]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async (e) => {
    if (e) e.preventDefault();
    if (!currentCase) {
      setError('No active forensic case selected. Please select or create a case first.');
      return;
    }
    if (!selectedFile) {
      setError('Please select a file to ingest.');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccessMsg(null);

    const formData = new FormData();
    formData.append('case_id', currentCase.id);
    formData.append('device', deviceName.trim() || 'Unknown Device');
    if (sourceType) formData.append('source_type', sourceType);
    formData.append('file', selectedFile);

    try {
      const res = await evidenceAPI.uploadEvidence(formData);
      const artCount = res.data.artifacts_created;
      setSuccessMsg(res.data.message || `Evidence ingested successfully (${artCount} artifacts created).`);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';

      // Rebuild timeline automatically after upload
      try {
        await timelineAPI.rebuildTimeline(currentCase.id);
      } catch (tlErr) {
        console.warn('Timeline auto-rebuild note:', tlErr);
      }

      // Refresh global case & dashboard state
      triggerRefresh();
      fetchEvidence();
    } catch (err) {
      console.error('Upload failed:', err);
      setError(err.response?.data?.detail || 'Failed to upload evidence file. Check file format and size.');
    } finally {
      setUploading(false);
    }
  };

  const handleQuickLoadSample = async (templateKey) => {
    const tmpl = SAMPLE_TEMPLATES[templateKey];
    if (!tmpl) return;

    const blob = new Blob([tmpl.content], { type: 'text/plain;charset=utf-8' });
    const file = new File([blob], tmpl.filename, { type: 'text/plain' });

    setSelectedFile(file);
    setDeviceName(tmpl.device);
    setSourceType(tmpl.source_type);

    if (!currentCase) {
      setError('Please create or select a case first to ingest this sample.');
      return;
    }

    // Direct upload
    setUploading(true);
    setError(null);
    setSuccessMsg(null);

    const formData = new FormData();
    formData.append('case_id', currentCase.id);
    formData.append('device', tmpl.device);
    formData.append('source_type', tmpl.source_type);
    formData.append('file', file);

    try {
      const res = await evidenceAPI.uploadEvidence(formData);
      setSuccessMsg(`Sample '${tmpl.filename}' successfully ingested (${res.data.artifacts_created} artifacts normalized).`);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';

      // Auto-rebuild timeline
      try {
        await timelineAPI.rebuildTimeline(currentCase.id);
      } catch (tlErr) {
        console.warn('Timeline rebuild note:', tlErr);
      }

      triggerRefresh();
      fetchEvidence();
    } catch (err) {
      console.error('Sample upload failed:', err);
      setError(err.response?.data?.detail || `Failed to ingest sample ${tmpl.filename}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadSample = (templateKey) => {
    const tmpl = SAMPLE_TEMPLATES[templateKey];
    if (!tmpl) return;

    const blob = new Blob([tmpl.content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = tmpl.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Remove this evidence item and associated normalized artifacts?')) return;
    try {
      await evidenceAPI.deleteEvidence(id);
      triggerRefresh();
      fetchEvidence();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete evidence');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Evidence Collection & Ingestion
          </h1>
          <p className="text-xs text-slate-500 font-medium mt-1">
            Upload raw forensic files (CSV, JSON, LOG, TXT, XML), compute SHA-256 custody hashes, and normalize telemetry.
          </p>
        </div>

        <button
          onClick={fetchEvidence}
          className="mt-3 sm:mt-0 inline-flex items-center px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors self-start"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Refresh List
        </button>
      </div>

      {/* No Case Warning Banner */}
      {!currentCase && (
        <div className="p-4 bg-amber-50 border border-amber-300 rounded-xl shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold text-amber-900">No Active Case Selected</h4>
              <p className="text-[11px] text-amber-800 mt-0.5">
                You must select or create a forensic case before uploading evidence files.
              </p>
            </div>
          </div>
          <button
            onClick={() => setCreateCaseModalOpen(true)}
            className="inline-flex items-center px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white text-xs font-bold rounded-lg shadow-xs transition-colors self-start sm:self-auto shrink-0"
          >
            <FolderPlus className="w-3.5 h-3.5 mr-1.5" />
            Create New Case
          </button>
        </div>
      )}

      {/* 1-Click Quick Ingestion for Forensic Samples */}
      <div className="p-5 bg-gradient-to-r from-blue-50/80 to-indigo-50/80 border border-blue-200 rounded-xl shadow-xs">
        <div className="flex items-center space-x-2 mb-3">
          <Sparkles className="w-4 h-4 text-blue-600" />
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Quick Ingest Realistic Forensic Samples
          </h3>
        </div>
        <p className="text-xs text-slate-600 mb-4">
          Test the timeline reconstruction and anti-forensics gap detector with pre-built forensic evidence templates. Click <strong>Ingest</strong> to upload directly into the active case:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {Object.entries(SAMPLE_TEMPLATES).map(([key, tmpl]) => (
            <div key={key} className="p-3 bg-white border border-slate-200 rounded-lg shadow-xs flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-xs text-slate-900 truncate">{tmpl.filename}</span>
                  <span className="text-[9px] font-extrabold uppercase px-1.5 py-0.5 bg-blue-100 text-blue-800 rounded">
                    {tmpl.source_type.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 leading-snug mb-3">
                  {tmpl.desc}
                </p>
              </div>

              <div className="flex items-center space-x-2 pt-2 border-t border-slate-100">
                <button
                  onClick={() => handleQuickLoadSample(key)}
                  disabled={uploading || !currentCase}
                  className="flex-1 py-1.5 px-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-[11px] rounded transition-colors disabled:opacity-50 text-center"
                >
                  ⚡ Ingest Sample
                </button>
                <button
                  onClick={() => handleDownloadSample(key)}
                  title="Download raw file"
                  className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Upload Box */}
      <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
        <h3 className="text-sm font-bold text-slate-800 tracking-tight mb-4 flex items-center">
          <Upload className="w-4 h-4 text-blue-600 mr-2" />
          Ingest Custom Forensic File
        </h3>

        {successMsg && (
          <div className="p-3 mb-4 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-center">
            <CheckCircle className="w-4 h-4 text-emerald-600 mr-2 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {error && (
          <div className="p-3 mb-4 bg-red-50 border border-red-200 rounded-lg text-xs text-red-800 flex items-center">
            <AlertCircle className="w-4 h-4 text-red-600 mr-2 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleUpload} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Target Device / Hostname *
              </label>
              <input
                type="text"
                required
                value={deviceName}
                onChange={(e) => setDeviceName(e.target.value)}
                placeholder="WORKSTATION-01"
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-xs font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Evidence Source Type (Optional)
              </label>
              <select
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-xs font-semibold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500 outline-none cursor-pointer"
              >
                <option value="">Auto-Detect from File Content</option>
                <option value="SYSTEM_LOGS">System Logs</option>
                <option value="BROWSER_ARTIFACTS">Browser Artifacts</option>
                <option value="FILE_METADATA">File Metadata</option>
                <option value="USB_LOGS">USB / Device Logs</option>
                <option value="NETWORK_LOGS">Network Logs</option>
                <option value="CLOUD_ACTIVITY">Cloud Activity</option>
                <option value="OTHER">Other</option>
              </select>
            </div>
          </div>

          {/* Drag & Drop Area */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
              dragActive ? 'border-blue-500 bg-blue-50/50' : 'border-slate-300 bg-slate-50/50 hover:bg-slate-100/50'
            }`}
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv,.json,.jsonl,.ndjson,.txt,.log,.xml"
              className="hidden"
              onChange={(e) => e.target.files && e.target.files[0] && setSelectedFile(e.target.files[0])}
            />

            <FileUp className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            {selectedFile ? (
              <div>
                <p className="text-xs font-bold text-slate-800">{selectedFile.name}</p>
                <p className="text-[11px] text-slate-400">{(selectedFile.size / 1024).toFixed(1)} KB — Click or drag to replace</p>
              </div>
            ) : (
              <div>
                <p className="text-xs font-bold text-slate-700">Click or drag & drop forensic file here</p>
                <p className="text-[11px] text-slate-400 mt-0.5">Supports CSV, JSON, LOG, TXT, XML up to 100MB</p>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={!selectedFile || uploading || !currentCase}
            className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-lg shadow-sm transition-colors disabled:opacity-50 flex items-center justify-center"
          >
            {uploading ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> Processing & Normalizing Evidence...
              </>
            ) : (
              'Upload and Process Evidence'
            )}
          </button>
        </form>
      </div>

      {/* Evidence Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between">
          <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Ingested Evidence Inventory ({evidenceList.length})
          </h3>
        </div>

        {loading && evidenceList.length === 0 ? (
          <LoadingState message="Loading evidence inventory..." />
        ) : evidenceList.length === 0 ? (
          <EmptyState
            title="No Evidence Ingested"
            description="Upload custom evidence files or use the quick sample buttons above to inspect forensic telemetry."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-100/60 text-slate-500 font-semibold uppercase tracking-wider">
                  <th className="py-3 px-4">ID</th>
                  <th className="py-3 px-4">Filename</th>
                  <th className="py-3 px-4">Source Type</th>
                  <th className="py-3 px-4">Device</th>
                  <th className="py-3 px-4">SHA-256 Hash</th>
                  <th className="py-3 px-4">Size</th>
                  <th className="py-3 px-4">Artifacts</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {evidenceList.map((ev) => (
                  <tr key={ev.id} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">EV-{ev.id}</td>
                    <td className="py-3 px-4 font-semibold text-slate-800 flex items-center">
                      <FileText className="w-4 h-4 text-blue-600 mr-2 shrink-0" />
                      {ev.filename}
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-600">{ev.source_type}</td>
                    <td className="py-3 px-4 text-slate-600">{ev.device}</td>
                    <td className="py-3 px-4 font-mono text-[10px] text-slate-500" title={ev.file_hash}>
                      {ev.file_hash.substring(0, 16)}...
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-mono">
                      {(ev.file_size / 1024).toFixed(1)} KB
                    </td>
                    <td className="py-3 px-4 font-bold text-blue-600">
                      {ev.artifacts_count || 0}
                    </td>
                    <td className="py-3 px-4">
                      <StatusBadge status={ev.status} />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleDelete(ev.id)}
                        className="p-1 text-slate-400 hover:text-red-600 rounded transition-colors"
                        title="Remove evidence"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Case Creation Modal */}
      <CreateCaseModal
        isOpen={createCaseModalOpen}
        onClose={() => setCreateCaseModalOpen(false)}
      />
    </div>
  );
};

export default EvidencePage;
