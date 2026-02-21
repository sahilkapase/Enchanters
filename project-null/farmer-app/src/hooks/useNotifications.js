import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationApi } from '../services/notificationApi';
import { useAuth } from '../context/AuthContext';

/** Paginated notification list */
export function useNotifications({ page = 1, perPage = 20, unreadOnly = false } = {}) {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['notifications', { page, perPage, unreadOnly }],
    queryFn: () =>
      notificationApi
        .getNotifications({ page, per_page: perPage, unread_only: unreadOnly })
        .then((res) => res.data),
    enabled: isAuthenticated,
    staleTime: 60_000, // 1 min
  });
}

/** Unread count for badge */
export function useUnreadCount() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['notifications', 'unread-count'],
    queryFn: () =>
      notificationApi.getUnreadCount().then((res) => res.data.unread_count),
    enabled: isAuthenticated,
    refetchInterval: 60_000,   // poll every 60s
    staleTime: 30_000,
  });
}

/** Mark a single notification as read */
export function useMarkRead() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (notificationId) => notificationApi.markRead(notificationId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}

/** Mark all notifications as read */
export function useMarkAllRead() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: () => notificationApi.markAllRead(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
}
