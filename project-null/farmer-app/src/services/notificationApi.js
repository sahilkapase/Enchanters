import api from './api';

export const notificationApi = {
  /** Paginated list (returns { items, unread_count, page, per_page, total }) */
  getNotifications: (params = {}) =>
    api.get('/notifications', { params }),

  /** Badge count — { unread_count } */
  getUnreadCount: () =>
    api.get('/notifications/unread-count'),

  /** Mark single notification read */
  markRead: (notificationId) =>
    api.post(`/notifications/${notificationId}/read`),

  /** Mark all notifications read */
  markAllRead: () =>
    api.post('/notifications/read-all'),
};
