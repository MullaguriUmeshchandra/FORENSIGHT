import axios from 'axios';

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api';
let cleanBaseUrl = rawBaseUrl.endsWith('/') ? rawBaseUrl.slice(0, -1) : rawBaseUrl;
if (cleanBaseUrl && !cleanBaseUrl.startsWith('http://') && !cleanBaseUrl.startsWith('https://') && !cleanBaseUrl.startsWith('/')) {
  cleanBaseUrl = `https://${cleanBaseUrl}`;
}
if (cleanBaseUrl.startsWith('http') && !cleanBaseUrl.endsWith('/api')) {
  cleanBaseUrl = `${cleanBaseUrl}/api`;
}
const API_BASE_URL = cleanBaseUrl;

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to append Bearer JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('forensics_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for automatic error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('forensics_token');
      localStorage.removeItem('forensics_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  register: (userData) => api.post('/auth/register', userData),
  me: () => api.get('/auth/me'),
};

export const caseAPI = {
  getCases: (skip = 0, limit = 100) => api.get(`/cases?skip=${skip}&limit=${limit}`),
  getCase: (id) => api.get(`/cases/${id}`),
  createCase: (data) => api.post('/cases', data),
  updateCase: (id, data) => api.put(`/cases/${id}`, data),
  deleteCase: (id) => api.delete(`/cases/${id}`),
};

export const dashboardAPI = {
  getSummary: (caseId) => api.get(`/dashboard/summary${caseId ? `?case_id=${caseId}` : ''}`),
  getActivity: (caseId, limit = 25) => api.get(`/dashboard/activity?limit=${limit}${caseId ? `&case_id=${caseId}` : ''}`),
};

export const evidenceAPI = {
  uploadEvidence: (formData) => api.post('/evidence/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getEvidence: (caseId) => api.get(`/evidence?case_id=${caseId}`),
  getEvidenceById: (id) => api.get(`/evidence/${id}`),
  deleteEvidence: (id) => api.delete(`/evidence/${id}`),
};

export const timelineAPI = {
  getTimeline: (caseId, skip = 0, limit = 500) => api.get(`/timeline?case_id=${caseId}&skip=${skip}&limit=${limit}`),
  rebuildTimeline: (caseId, options = {}) => api.post('/timeline/rebuild', { case_id: caseId, ...options }),
};

export const gapAPI = {
  getGaps: (caseId) => api.get(`/gaps?case_id=${caseId}`),
  detectGaps: (caseId) => api.post(`/gaps/detect?case_id=${caseId}`),
};

export const contradictionAPI = {
  getContradictions: (caseId) => api.get(`/contradictions?case_id=${caseId}`),
  detectContradictions: (caseId) => api.post(`/contradictions/detect?case_id=${caseId}`),
};

export const recommendationAPI = {
  getRecommendations: (caseId) => api.get(`/recommendations?case_id=${caseId}`),
  generateRecommendations: (caseId) => api.post(`/recommendations/generate?case_id=${caseId}`),
  updateRecommendation: (id, data) => api.put(`/recommendations/${id}`, data),
};

export const investigationAPI = {
  getOverview: (caseId) => api.get(`/investigation/overview?case_id=${caseId}`),
  getRelationships: (caseId) => api.get(`/investigation/relationships?case_id=${caseId}`),
};

export const reportAPI = {
  getReports: (caseId) => api.get(`/reports?case_id=${caseId}`),
  generateReport: (caseId, title, format = 'MARKDOWN') => api.post('/reports', { case_id: caseId, title, report_format: format }),
  downloadReport: (id) => api.get(`/reports/${id}/download`, { responseType: 'blob' }),
  getDownloadUrl: (id) => {
    const token = localStorage.getItem('forensics_token');
    return `${API_BASE_URL}/reports/${id}/download${token ? `?token=${encodeURIComponent(token)}` : ''}`;
  },
};

export default api;
