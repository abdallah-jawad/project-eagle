import { CustomerConfig } from './types';

export const customerConfigs: CustomerConfig[] = [
  {
    id: 'customer1',
    name: 'Acme Corp',
    region: 'us-east-1',
    cameras: [
      {
        id: 'cam1',
        name: 'Main Entrance',
        rtspUrl: 'rtsp://camera1.example.com/stream1',
        streamName: 'acme-main-entrance',
        resolution: {
          width: 1920,
          height: 1080
        },
        fps: 30,
        bitrate: 4000,
        location: 'Main Building Entrance',
        description: '24/7 surveillance of main entrance'
      },
      {
        id: 'cam2',
        name: 'Parking Lot',
        rtspUrl: 'rtsp://camera2.example.com/stream1',
        streamName: 'acme-parking-lot',
        resolution: {
          width: 1920,
          height: 1080
        },
        fps: 30,
        bitrate: 4000,
        location: 'North Parking Lot',
        description: 'Parking lot surveillance'
      }
    ]
  }
]; 