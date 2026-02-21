import api from './api';

export const insuranceApi = {
  /** List all active insurance plans */
  getPlans() {
    return api.get('/insurance/plans');
  },

  /** Get plan detail */
  getPlan(id) {
    return api.get(`/insurance/plans/${id}`);
  },

  /** Generate auto-filled PDF form */
  generateForm(planId) {
    return api.post(`/insurance/plans/${planId}/generate-form`);
  },
};
