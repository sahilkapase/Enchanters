import api from './api';

export const subsidyApi = {
  /**
   * List subsidies with filters
   * @param {{ category?, state?, status? }} params
   */
  getSubsidies(params = {}) {
    return api.get('/subsidies', { params });
  },

  /** Get subsidy detail */
  getSubsidy(id) {
    return api.get(`/subsidies/${id}`);
  },

  /**
   * Get calendar view of deadlines
   * @param {{ month, year }} params
   */
  getCalendar(params) {
    return api.get('/subsidies/calendar', { params });
  },

  /** Set deadline reminder */
  setReminder(id, data) {
    return api.post(`/subsidies/${id}/remind`, data);
  },
};
