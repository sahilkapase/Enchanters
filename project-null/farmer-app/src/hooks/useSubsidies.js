import { useQuery, useMutation } from '@tanstack/react-query';
import { subsidyApi } from '../services/subsidyApi';
import { useAuth } from '../context/AuthContext';

export function useSubsidies(filters = {}) {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['subsidies', filters],
    queryFn: () => subsidyApi.getSubsidies(filters).then((res) => res.data),
    enabled: isAuthenticated,
    staleTime: 10 * 60 * 1000,
  });
}

export function useSubsidyDetail(id) {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['subsidies', id],
    queryFn: () => subsidyApi.getSubsidy(id).then((res) => res.data),
    enabled: isAuthenticated && !!id,
  });
}

export function useSubsidyCalendar(params) {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['subsidies', 'calendar', params],
    queryFn: () => subsidyApi.getCalendar(params).then((res) => res.data),
    enabled: isAuthenticated && !!params?.month && !!params?.year,
  });
}

export function useSetSubsidyReminder() {
  return useMutation({
    mutationFn: ({ id, data }) => subsidyApi.setReminder(id, data).then((res) => res.data),
  });
}
