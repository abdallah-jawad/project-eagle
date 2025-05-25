import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as codedeploy from 'aws-cdk-lib/aws-codedeploy';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { SecretValue } from 'aws-cdk-lib';
import { GitHubConfig } from '../config/deployment-config';

export interface DeploymentStackProps extends cdk.StackProps {
  instance: cdk.aws_ec2.Instance;
  github: GitHubConfig;
  watchDirectory: string;
  applicationName: string;
  pipelineName: string;
}

export class DeploymentStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: DeploymentStackProps) {
    super(scope, id, props);

    // Create CodeDeploy application
    const application = new codedeploy.ServerApplication(this, 'Application', {
      applicationName: props.applicationName
    });

    // Create IAM role for CodeDeploy
    const codeDeployRole = new iam.Role(this, 'CodeDeployRole', {
      assumedBy: new iam.ServicePrincipal('codedeploy.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AWSCodeDeployRoleForEC2')
      ]
    });

    // Create deployment group
    const deploymentGroup = new codedeploy.ServerDeploymentGroup(this, 'DeploymentGroup', {
      application,
      deploymentConfig: codedeploy.ServerDeploymentConfig.ALL_AT_ONCE,
      ec2InstanceTags: new codedeploy.InstanceTagSet({
        'Name': [props.instance.instanceId]
      }),
      role: codeDeployRole,
      autoRollback: {
        failedDeployment: true,
        stoppedDeployment: true
      }
    });

    // Create pipeline
    const pipeline = new codepipeline.Pipeline(this, 'Pipeline', {
      pipelineName: props.pipelineName,
      stages: [
        {
          stageName: 'Source',
          actions: [
            new codepipeline_actions.GitHubSourceAction({
              actionName: 'GitHub_Source',
              owner: props.github.owner,
              repo: props.github.repo,
              branch: props.github.branch,
              oauthToken: SecretValue.secretsManager(props.github.tokenSecretName),
              output: new codepipeline.Artifact('SourceOutput'),
              variablesNamespace: 'SourceVariables',
              // Only trigger on changes to the specified directory
              filters: [
                {
                  jsonPath: '$.commits[*].modified[*]',
                  matchEquals: `${props.watchDirectory}/**`
                },
                {
                  jsonPath: '$.commits[*].added[*]',
                  matchEquals: `${props.watchDirectory}/**`
                },
                {
                  jsonPath: '$.commits[*].removed[*]',
                  matchEquals: `${props.watchDirectory}/**`
                }
              ]
            })
          ]
        },
        {
          stageName: 'Deploy',
          actions: [
            new codepipeline_actions.CodeDeployServerDeployAction({
              actionName: 'CodeDeploy',
              input: new codepipeline.Artifact('SourceOutput'),
              deploymentGroup
            })
          ]
        }
      ]
    });

    // Output the pipeline URL
    new cdk.CfnOutput(this, 'PipelineUrl', {
      value: `https://${this.region}.console.aws.amazon.com/codepipeline/home?region=${this.region}#/view/${pipeline.pipelineName}`,
      description: 'URL of the deployment pipeline'
    });
  }
} 