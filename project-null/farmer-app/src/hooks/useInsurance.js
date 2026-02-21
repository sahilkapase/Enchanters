import { useQuery, useMutation } from '@tanstack/react-query';
import { insuranceApi } from '../services/insuranceApi';
import { useAuth } from '../context/AuthContext';

export function useInsurancePlans() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['insurance', 'plans'],
    queryFn: () => insuranceApi.getPlans().then((res) => res.data),
    enabled: isAuthenticated,
    staleTime: 30 * 60 * 1000,
  });
}

export function useInsurancePlanDetail(id) {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['insurance', 'plans', id],
    queryFn: () => insuranceApi.getPlan(id).then((res) => res.data),
    enabled: isAuthenticated && !!id,
  });
}

export function useGenerateInsuranceForm() {
  return useMutation({
    mutationFn: (planId) => insuranceApi.generateForm(planId).then((res) => res.data),
    onSuccess: (data) => {
      // Backend returns { file_key, file_name, download_url, message }
      const url = data.download_url || `/api/v1/files/${data.file_key}`;
      const a = document.createElement('a');
      a.href = url;
      a.download = data.file_name || 'insurance-form.pdf';
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      a.remove();
    },
  });
}
