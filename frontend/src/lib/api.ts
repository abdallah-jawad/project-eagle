import axios from 'axios';

const isLocal = process.env.NEXT_PUBLIC_IS_LOCAL === 'true';
export const API_BASE_URL = isLocal 
  ? 'http://localhost:8080/api/v1'
  : 'http://3.93.248.72:8080/api/v1';

// Create axios instance with default config
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to add auth token to requests
api.interceptors.request.use((config) => {
  // Get the auth token from cookies
  const cookies = document.cookie.split(';');
  const authCookie = cookies.find(cookie => cookie.trim().startsWith('auth-token='));
  
  if (authCookie) {
    const token = authCookie.split('=')[1];
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  
  return config;
});

export const authApi = {
  login: async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post('/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
}; 