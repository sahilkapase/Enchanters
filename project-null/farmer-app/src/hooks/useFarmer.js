import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { farmerApi } from '../services/farmerApi';
import { useAuth } from '../context/AuthContext';

export function useFarmerProfile() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['farmer', 'me'],
    queryFn: () => farmerApi.getMe().then((res) => res.data),
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000,
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const { updateFarmerLocal } = useAuth();

  return useMutation({
    mutationFn: (data) => farmerApi.updateMe(data).then((res) => res.data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['farmer', 'me'] });
      // Re-match: profile changes affect scheme/subsidy eligibility
      queryClient.invalidateQueries({ queryKey: ['schemes'] });
      queryClient.invalidateQueries({ queryKey: ['subsidies'] });
      updateFarmerLocal(data);
    },
  });
}

export function useUpdateExtendedProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => farmerApi.updateProfile(data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farmer', 'me'] });
      // Re-match: irrigation/ownership changes affect eligibility
      queryClient.invalidateQueries({ queryKey: ['schemes'] });
      queryClient.invalidateQueries({ queryKey: ['subsidies'] });
    },
  });
}

export function useFarmerCrops() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['farmer', 'crops'],
    queryFn: () => farmerApi.getCrops().then((res) => res.data),
    enabled: isAuthenticated,
  });
}

export function useAddCrop() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data) => farmerApi.addCrop(data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farmer', 'crops'] });
      queryClient.invalidateQueries({ queryKey: ['farmer', 'me'] });
      // Re-match: crop changes affect scheme eligibility
      queryClient.invalidateQueries({ queryKey: ['schemes'] });
      queryClient.invalidateQueries({ queryKey: ['subsidies'] });
    },
  });
}

export function useRemoveCrop() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (cropId) => farmerApi.removeCrop(cropId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farmer', 'crops'] });
      queryClient.invalidateQueries({ queryKey: ['farmer', 'me'] });
      queryClient.invalidateQueries({ queryKey: ['schemes'] });
      queryClient.invalidateQueries({ queryKey: ['subsidies'] });
    },
  });
}

export function useFarmerDocuments() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['farmer', 'documents'],
    queryFn: () => farmerApi.getDocuments().then((res) => res.data),
    enabled: isAuthenticated,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ file, docType }) => farmerApi.uploadDocument(file, docType).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farmer', 'documents'] });
    },
  });
}

export function useDeleteDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (docId) => farmerApi.deleteDocument(docId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['farmer', 'documents'] });
    },
  });
}

export function useAccessLog() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['farmer', 'access-log'],
    queryFn: () => farmerApi.getAccessLog().then((res) => res.data),
    enabled: isAuthenticated,
  });
}

export function useGeneratedForms() {
  const { isAuthenticated } = useAuth();

  return useQuery({
    queryKey: ['farmer', 'forms'],
    queryFn: () => farmerApi.getForms().then((res) => res.data),
    enabled: isAuthenticated,
  });
}
