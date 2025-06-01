import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';

export interface AuthStackProps extends cdk.StackProps {
  environment: string;
}

export class AuthStack extends cdk.Stack {
  public readonly userTable: dynamodb.Table;
  public readonly jwtSecret: secretsmanager.Secret;

  constructor(scope: Construct, id: string, props: AuthStackProps) {
    super(scope, id, props);

    // Create DynamoDB table for users
    this.userTable = new dynamodb.Table(this, 'UsersTable', {
      tableName: `${props.environment}-users`,
      partitionKey: { name: 'email', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      pointInTimeRecovery: true,
    });

    // Create JWT secret in Secrets Manager
    this.jwtSecret = new secretsmanager.Secret(this, 'JwtSecret', {
      secretName: `${props.environment}/jwt-secret`,
      description: 'JWT secret for authentication',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ secret: '' }),
        generateStringKey: 'secret',
        excludeCharacters: '{}[]()\'"/\\@:',
      },
    });

    // Output the table name and secret ARN
    new cdk.CfnOutput(this, 'UserTableName', {
      value: this.userTable.tableName,
      description: 'Name of the users DynamoDB table',
    });

    new cdk.CfnOutput(this, 'JwtSecretArn', {
      value: this.jwtSecret.secretArn,
      description: 'ARN of the JWT secret in Secrets Manager',
    });
  }
} 