import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
export interface RtspKvsStackProps extends cdk.StackProps {
    myIpAddress: string;
    keyPairName: string;
}
export declare class RtspKvsStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props: RtspKvsStackProps);
    private calculateInstanceType;
    private getInstanceSize;
}
