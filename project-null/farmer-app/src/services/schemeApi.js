import api from './api';

export const schemeApi = {
  /**
   * List schemes with filters
   * @param {{ crop?, season?, state?, district?, land_area?, sort? }} params
   */
  getSchemes(params = {}) {
    return api.get('/schemes', { params });
  },

  /** Get scheme detail */
  getScheme(id) {
    return api.get(`/schemes/${id}`);
  },

  /** Check eligibility for a scheme */
  checkEligibility(id) {
    return api.get(`/schemes/${id}/eligibility`);
  },

  /** Generate auto-filled PDF form */
  generateForm(id) {
    return api.post(`/schemes/${id}/generate-form`);
  },

  /** Set deadline reminder */
  setReminder(id, data) {
    return api.post(`/schemes/${id}/remind`, data);
  },
};
