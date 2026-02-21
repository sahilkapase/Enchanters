import { useQuery, useMutation } from '@tanstack/react-query';
import { schemeApi } from '../services/schemeApi';
import { useAuth } from '../context/AuthContext';

export function useSchemes(filters = {}) {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['schemes', filters],
    queryFn: () => schemeApi.getSchemes(filters).then((res) => res.data),
    enabled: isAuthenticated,
    staleTime: 10 * 60 * 1000,
  });
}

export function useSchemeDetail(id) {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['schemes', id],
    queryFn: () => schemeApi.getScheme(id).then((res) => res.data),
    enabled: isAuthenticated && !!id,
  });
}

export function useSchemeEligibility(id) {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['schemes', id, 'eligibility'],
    queryFn: () => schemeApi.checkEligibility(id).then((res) => res.data),
    enabled: isAuthenticated && !!id,
  });
}

export function useGenerateSchemeForm() {
  return useMutation({
    mutationFn: (id) => schemeApi.generateForm(id).then((res) => res.data),
    onSuccess: (data) => {
      // Backend returns { file_key, file_name, download_url, message }
      const url = data.download_url || `/api/v1/files/${data.file_key}`;
      const a = document.createElement('a');
      a.href = url;
      a.download = data.file_name || 'scheme-form.pdf';
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      a.remove();
    },
  });
}

export function useSetSchemeReminder() {
  return useMutation({
    mutationFn: ({ id, data }) => schemeApi.setReminder(id, data).then((res) => res.data),
  });
}
