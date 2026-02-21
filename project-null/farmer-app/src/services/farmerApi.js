import api from './api';

export const farmerApi = {
  /** Get current farmer profile */
  getMe() {
    return api.get('/farmers/me');
  },

  /** Update basic farmer info */
  updateMe(data) {
    return api.patch('/farmers/me', data);
  },

  /** Create/update extended profile (aadhaar, bank, etc.) */
  updateProfile(data) {
    return api.put('/farmers/me/profile', data);
  },

  /** List farmer's crops */
  getCrops() {
    return api.get('/farmers/me/crops');
  },

  /** Add a crop */
  addCrop(data) {
    return api.post('/farmers/me/crops', data);
  },

  /** Remove a crop */
  removeCrop(cropId) {
    return api.delete(`/farmers/me/crops/${cropId}`);
  },

  /** Upload a document (multipart) */
  uploadDocument(file, docType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);
    return api.post('/farmers/me/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  /** List uploaded documents */
  getDocuments() {
    return api.get('/farmers/me/documents');
  },

  /** Delete a document */
  deleteDocument(docId) {
    return api.delete(`/farmers/me/documents/${docId}`);
  },

  /** Get agent access log */
  getAccessLog() {
    return api.get('/farmers/me/access-log');
  },

  /** Get generated forms history */
  getForms() {
    return api.get('/farmers/me/forms');
  },
};
