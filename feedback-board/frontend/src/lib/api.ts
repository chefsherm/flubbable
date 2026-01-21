import axios from 'axios';
import { auth } from './firebase';
import type { FeatureRequest, CreateFeatureRequestDto } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const featureRequestsApi = {
  getAll: async (): Promise<FeatureRequest[]> => {
    const response = await api.get('/feature-requests');
    return response.data;
  },

  getById: async (id: string): Promise<FeatureRequest> => {
    const response = await api.get(`/feature-requests/${id}`);
    return response.data;
  },

  create: async (data: CreateFeatureRequestDto): Promise<FeatureRequest> => {
    const response = await api.post('/feature-requests', data);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/feature-requests/${id}`);
  },

  vote: async (id: string): Promise<FeatureRequest> => {
    const response = await api.post(`/feature-requests/${id}/vote`);
    return response.data;
  },

  unvote: async (id: string): Promise<FeatureRequest> => {
    const response = await api.delete(`/feature-requests/${id}/vote`);
    return response.data;
  },
};

export const usersApi = {
  getMe: async () => {
    const response = await api.get('/users/me');
    return response.data;
  },
};

export default api;
