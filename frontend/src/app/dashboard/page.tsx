'use client';

import { useCameraConfigurations } from '@/hooks/useCameraConfigurations';

export default function Dashboard() {
  const { cameras, loading, error } = useCameraConfigurations();

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
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Camera Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cameras.map((camera) => (
          <div key={camera.camera_id} className="bg-white p-6 rounded-lg shadow-lg">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-lg font-semibold">{camera.zone}</h3>
              <span className={`px-2 py-1 rounded text-sm ${
                camera.status === 'active' ? 'bg-green-100 text-green-800' :
                camera.status === 'inactive' ? 'bg-gray-100 text-gray-800' :
                'bg-red-100 text-red-800'
              }`}>
                {camera.status}
              </span>
            </div>
            <div className="space-y-2">
              <p className="text-gray-600">
                <span className="font-medium">FPS:</span> {camera.fps}
              </p>
              <p className="text-gray-600">
                <span className="font-medium">Resolution:</span> {camera.resolution.width}x{camera.resolution.height}
              </p>
              {camera.labels.length > 0 && (
                <div>
                  <p className="font-medium text-gray-600 mb-1">Labels:</p>
                  <div className="flex flex-wrap gap-2">
                    {camera.labels.map((label) => (
                      <span key={label} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                        {label}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {camera.notification_settings.enabled && (
                <div className="mt-4 pt-4 border-t">
                  <p className="font-medium text-gray-600 mb-1">Notifications:</p>
                  <p className="text-sm text-gray-600">
                    {camera.notification_settings.notify_start_time} - {camera.notification_settings.notify_end_time}
                  </p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 