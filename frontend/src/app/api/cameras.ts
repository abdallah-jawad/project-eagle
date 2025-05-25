import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface Camera {
  id: string;
  name: string;
  description: string;
  rtsp_url: string;
  kvs_stream_id?: string;
  status: 'active' | 'inactive';
}

export const cameraApi = {
  /**
   * Fetch all cameras for a specific client
   * @param clientId - The ID of the client to fetch cameras for
   */
  getCameras: async (clientId: string): Promise<Camera[]> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/cameras`, {
        params: { client_id: clientId }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching cameras:', error);
      throw error;
    }
  },

  /**
   * Fetch a specific camera by ID
   * @param cameraId - The ID of the camera to fetch
   */
  getCamera: async (cameraId: string): Promise<Camera> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/cameras/${cameraId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching camera ${cameraId}:`, error);
      throw error;
    }
  }
}; 