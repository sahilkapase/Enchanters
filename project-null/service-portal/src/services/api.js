import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

/* ── Attach agent JWT on every request ── */
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('agent_access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

/* ── Auto-refresh on 401 ── */
let refreshing = null;
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    const orig = err.config;
    if (err.response?.status === 401 && !orig._retry) {
      orig._retry = true;
      if (!refreshing) {
        const rt = localStorage.getItem('agent_refresh_token');
        refreshing = api
          .post('/service/auth/refresh', { refresh_token: rt })
          .then((r) => {
            localStorage.setItem('agent_access_token', r.data.access_token);
            localStorage.setItem('agent_refresh_token', r.data.refresh_token);
            return r.data.access_token;
          })
          .catch(() => {
            localStorage.clear();
            window.location.href = '/login';
            return null;
          })
          .finally(() => { refreshing = null; });
      }
      const token = await refreshing;
      if (token) {
        orig.headers.Authorization = `Bearer ${token}`;
        return api(orig);
      }
    }
    return Promise.reject(err);
  }
);

export default api;

/* ── Agent Auth ── */
export const agentLogin = (data) => api.post('/service/auth/login', data).then(r => r.data);
export const agentLogout = () => api.post('/service/auth/logout').then(r => r.data);

/* ── Farmer lookup ── */
export const lookupFarmer = (query) => api.post('/service/lookup', { query }).then(r => r.data);

/* ── Agent session (consent-based) ── */
export const requestAccess = (farmerId, purpose) =>
  api.post('/service/request-access', { farmer_id: farmerId, purpose }).then(r => r.data);
export const verifyAccess = (farmerId, otp) =>
  api.post('/service/verify-access', { farmer_id: farmerId, otp }).then(r => r.data);
export const getSession = (sessionId) =>
  api.get(`/service/session/${sessionId}`).then(r => r.data);
export const endSession = (sessionId) =>
  api.post(`/service/session/${sessionId}/end`).then(r => r.data);

/* ── Farmer data (via active session) ── */
export const getSessionFarmer = (sessionId) =>
  api.get(`/service/session/${sessionId}/farmer`).then(r => r.data);
export const generateFormForSession = (sessionId, payload) =>
  api.post(`/service/session/${sessionId}/generate-form`, payload).then(r => r.data);

/* ── Activity log ── */
export const getAgentActivity = (params) =>
  api.get('/service/activity', { params }).then(r => r.data);

/* ── Staging Queue ── */
export const getStagedItems = (params) =>
  api.get('/staging', { params }).then(r => r.data);
export const getStagedItem = (id) =>
  api.get(`/staging/${id}`).then(r => r.data);
export const createStagedItem = (data) =>
  api.post('/staging', data).then(r => r.data);
export const updateStagedItem = (id, data) =>
  api.patch(`/staging/${id}`, data).then(r => r.data);
export const approveStagedItem = (id, data) =>
  api.post(`/staging/${id}/approve`, data).then(r => r.data);
export const rejectStagedItem = (id, data) =>
  api.post(`/staging/${id}/reject`, data).then(r => r.data);
export const getPendingCount = () =>
  api.get('/staging/pending-count').then(r => r.data);
