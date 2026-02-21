import api from './api';

export const locationApi = {
  /** Resolve PIN code to district/state */
  resolvePin(pincode) {
    return api.get(`/location/pin/${pincode}`);
  },

  /** List all states */
  getStates() {
    return api.get('/location/states');
  },

  /** List districts for a state */
  getDistricts(state) {
    return api.get(`/location/districts/${encodeURIComponent(state)}`);
  },
};
