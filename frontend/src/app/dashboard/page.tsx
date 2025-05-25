'use client';

import { useEffect, useState } from 'react';
import { cameraApi, Camera } from '../api/cameras';

export default function Dashboard() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCameras = async () => {
      try {
        // For now, using a hardcoded client ID. In a real app, this would come from authentication
        const clientId = 'customer1';
        const data = await cameraApi.getCameras(clientId);
        setCameras(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch cameras. Please try again later.');
        console.error('Error fetching cameras:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCameras();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-xl">Loading cameras...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-xl text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <h1 className="mb-8 text-4xl font-bold text-black">Cameras</h1>
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {cameras.map((camera) => (
          <div
            key={camera.id}
            className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm"
          >
            <h2 className="mb-2 text-xl font-semibold">{camera.name}</h2>
            <p className="mb-4 text-gray-600">{camera.description}</p>
            <div className="flex items-center justify-between">
              <span
                className={`rounded-full px-3 py-1 text-sm ${
                  camera.status === 'active'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}
              >
                {camera.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 