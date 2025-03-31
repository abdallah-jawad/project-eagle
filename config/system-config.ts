import { SystemConfig } from './types';

export const systemConfig: SystemConfig = {
  defaultInstanceType: 't3.medium',
  maxCamerasPerInstance: 10,
  instanceTypes: {
    't3.small': {
      vcpus: 2,
      memoryGiB: 2,
      maxCameras: 5
    },
    't3.medium': {
      vcpus: 2,
      memoryGiB: 4,
      maxCameras: 10
    },
    't3.large': {
      vcpus: 2,
      memoryGiB: 8,
      maxCameras: 20
    },
    't3.xlarge': {
      vcpus: 4,
      memoryGiB: 16,
      maxCameras: 40
    }
  }
}; 