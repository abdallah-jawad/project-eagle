export interface CameraConfig {
    id: string;
    name: string;
    rtspUrl: string;
    streamName: string;
    resolution?: {
        width: number;
        height: number;
    };
    fps?: number;
    bitrate?: number;
    location?: string;
    description?: string;
}
export interface CustomerConfig {
    id: string;
    name: string;
    cameras: CameraConfig[];
    region: string;
    instanceType?: string;
}
export interface SystemConfig {
    defaultInstanceType: string;
    maxCamerasPerInstance: number;
    instanceTypes: {
        [key: string]: {
            vcpus: number;
            memoryGiB: number;
            maxCameras: number;
        };
    };
}
