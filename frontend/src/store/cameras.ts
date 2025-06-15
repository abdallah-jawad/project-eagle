'use client';

import { create } from 'zustand';
import { api } from '@/lib/api';

interface Camera {
  camera_id: string;
  client_id: string;
  enabled: boolean;
  zone: string;
  rtsp_url: string;
  notification_settings: {
    labels_to_notify_on: string[];
    contact_email: string;
    contact_phone: string;
    notify_start_time: string;
    notify_end_time: string;
    enabled: boolean;
  };
  fps: number;
  resolution: {
    width: number;
    height: number;
  };
  kvs_stream_id?: string;
  labels: string[];
  status: 'active' | 'inactive' | 'error';
}

interface CameraState {
  cameras: Camera[];
  loading: boolean;
  error: string | null;
  fetchCameras: (clientId: string) => Promise<void>;
  clearCameras: () => void;
}

export const useCameraStore = create<CameraState>((set) => ({
  cameras: [],
  loading: false,
  error: null,
  fetchCameras: async (clientId: string) => {
    try {
      set({ loading: true, error: null });
      const response = await api.get(`/cameras?client_id=${clientId}`);
      set({ cameras: response.data, loading: false });
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Failed to fetch camera configurations',
        loading: false 
      });
    }
  },
  clearCameras: () => set({ cameras: [], error: null }),
})); 