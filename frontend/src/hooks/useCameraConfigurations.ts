'use client';

import { useEffect, useRef } from 'react';
import { useAuthStore } from '@/store/auth';
import { useCameraStore } from '@/store/cameras';

export const useCameraConfigurations = () => {
  const { user } = useAuthStore();
  const { cameras, loading, error, fetchCameras, clearCameras } = useCameraStore();
  const hasFetched = useRef(false);

  useEffect(() => {
    // Only fetch if we have a user and haven't fetched yet
    if (user?.id && !hasFetched.current) {
      hasFetched.current = true;
      fetchCameras(user.id);
    } else if (!user?.id) {
      hasFetched.current = false;
      clearCameras();
    }
  }, [user?.id, fetchCameras, clearCameras]);

  return {
    cameras,
    loading,
    error,
  };
}; 