import * as cdk from 'aws-cdk-lib';
import * as kinesisvideo from 'aws-cdk-lib/aws-kinesisvideo';
import * as path from 'path';
import * as appconfig from 'aws-cdk-lib/aws-appconfig';
import { Construct } from 'constructs';
import * as fs from 'fs';
import { CameraConfig } from './interfaces/camera-config';

export class KvsStack extends cdk.Stack {
  public readonly cameraConfigs: CameraConfig;
  public readonly appConfigApp: appconfig.CfnApplication;
  public readonly appConfigEnv: appconfig.CfnEnvironment;
  public readonly appConfigProfile: appconfig.CfnConfigurationProfile;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Load camera configuration
    this.cameraConfigs = JSON.parse(
      fs.readFileSync(path.join(__dirname, '../config/camera-config.json'), 'utf-8')
    );

    // Create KVS streams for all enabled cameras
    const streams: { [key: string]: kinesisvideo.CfnStream } = {};
    this.cameraConfigs.cameras
      .filter(camera => camera.enabled)
      .forEach(camera => {
        streams[camera.kvs_stream_id] = new kinesisvideo.CfnStream(this, `KvsStream-${camera.kvs_stream_id}`, {
          name: camera.kvs_stream_id,
          dataRetentionInHours: 24,
          mediaType: 'video/h264',
        });
      });

    // Create AppConfig application
    this.appConfigApp = new appconfig.CfnApplication(this, 'ComputerVisionApp', {
      name: 'computer-vision',
      description: 'Computer Vision application configuration'
    });

    // Create AppConfig environment
    this.appConfigEnv = new appconfig.CfnEnvironment(this, 'ComputerVisionEnv', {
      applicationId: this.appConfigApp.ref,
      name: 'production',
      description: 'Production environment for Computer Vision application'
    });

    // Create AppConfig configuration profile
    this.appConfigProfile = new appconfig.CfnConfigurationProfile(this, 'CameraConfigProfile', {
      applicationId: this.appConfigApp.ref,
      name: 'camera-config',
      description: 'Camera configuration profile',
      locationUri: 'hosted'
    });
  }
}
