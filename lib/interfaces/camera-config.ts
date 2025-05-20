export interface Resolution {
  width: number;
  height: number;
}

export interface NotificationSettings {
  labels_to_notify_on: string[];
  contact_email: string;
  contact_phone: string;
  notify_start_time: string;
  notify_end_time: string;
  enabled: boolean;
}

export interface Camera {
  camera_id: string;
  client_id: string;
  enabled: boolean;
  zone: string;
  rtsp_url: string;
  notification_settings: NotificationSettings;
  fps: number;
  resolution: Resolution;
  kvs_stream_id: string;
  labels: string[];
}

export interface CameraConfig {
  cameras: Camera[];
} 