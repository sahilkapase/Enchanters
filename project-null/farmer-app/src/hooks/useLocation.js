import { useQuery } from '@tanstack/react-query';
import { locationApi } from '../services/locationApi';

export function usePinCodeLookup(pincode) {
  return useQuery({
    queryKey: ['location', 'pin', pincode],
    queryFn: () => locationApi.resolvePin(pincode).then((res) => res.data),
    enabled: !!pincode && /^[1-9]\d{5}$/.test(pincode),
    staleTime: 60 * 60 * 1000, // cache for 1 hour
    retry: 1,
  });
}

export function useStates() {
  return useQuery({
    queryKey: ['location', 'states'],
    queryFn: () => locationApi.getStates().then((res) => res.data.states ?? res.data),
    staleTime: 24 * 60 * 60 * 1000, // cache for 24 hours
  });
}

export function useDistricts(state) {
  return useQuery({
    queryKey: ['location', 'districts', state],
    queryFn: () => locationApi.getDistricts(state).then((res) => res.data.districts ?? res.data),
    enabled: !!state,
    staleTime: 24 * 60 * 60 * 1000,
  });
}
