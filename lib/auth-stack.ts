import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as appconfig from 'aws-cdk-lib/aws-appconfig';

export interface AuthStackProps extends cdk.StackProps {
  environment: string;
}

export class AuthStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: AuthStackProps) {
    super(scope, id, props);

    // Create DynamoDB table for users
    const userTable = new dynamodb.Table(this, 'UsersTable', {
      tableName: `users`,
      partitionKey: { name: 'email', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      pointInTimeRecovery: true,
    });

    // Create JWT secret in Secrets Manager
    const jwtSecret = new secretsmanager.Secret(this, 'JwtSecret', {
      secretName: `jwt-secret`,
      description: 'JWT secret for authentication',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ secret: '' }),
        generateStringKey: 'secret',
        excludeCharacters: '{}[]()\'"/\\@:',
      },
    });

    // Create AppConfig resources
    const appConfigApp = new appconfig.CfnApplication(this, 'AppConfigApp', {
      name: 'computer-vision-app',
      description: 'Application configuration for computer vision service',
    });

    const appConfigEnv = new appconfig.CfnEnvironment(this, 'AppConfigEnv', {
      applicationId: appConfigApp.ref,
      name: props.environment,
      description: `Environment configuration for ${props.environment}`,
    });

    const appConfigProfile = new appconfig.CfnConfigurationProfile(this, 'AppConfigProfile', {
      applicationId: appConfigApp.ref,
      name: 'computer-vision-config',
      description: 'Configuration profile for computer vision service',
      locationUri: 'hosted',
    });
  }
} 