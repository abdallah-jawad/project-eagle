import { CustomerConfig } from './types';

export const customerConfigs: CustomerConfig[] = [
  {
    id: 'customer1',
    name: 'Acme Corp',
    region: 'us-east-1',
    cameras: [
      {
        id: 'cam1',
        name: 'Test Camera 1',
        rtspUrl: 'rtsp://admin:ProjectEagle%40AC@70.175.157.61:554',
        streamName: 'test-camera-1',
        resolution: {
          width: 1920,
          height: 1080
        },
        fps: 30,
        bitrate: 4000,
        location: 'Test Location 1',
        description: 'Test Description 1'
      },
    ]
  }
]; 