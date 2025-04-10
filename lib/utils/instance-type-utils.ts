import * as ec2 from 'aws-cdk-lib/aws-ec2';
import { systemConfig } from '../../config/system-config';
import { customerConfigs } from '../../config/customer-configs';

/**
 * Utility class for EC2 instance type calculations
 */
export class InstanceTypeUtils {
  /**
   * Calculate the total number of cameras across all customers
   * @returns The total number of cameras
   */
  public static calculateTotalCameras(): number {
    return customerConfigs.reduce((sum, customer) => sum + customer.cameras.length, 0);
  }

  /**
   * Determine the appropriate instance type based on the number of cameras
   * @param numCameras The number of cameras to handle
   * @returns The recommended instance type (e.g., 't3.medium')
   */
  public static calculateInstanceType(numCameras: number): string {
    // Find the smallest instance type that can handle the number of cameras
    for (const [type, specs] of Object.entries(systemConfig.instanceTypes)) {
      if (specs.maxCameras >= numCameras) {
        return type;
      }
    }
    // If no instance type can handle the number of cameras, throw an error
    throw new Error(`No instance type available to handle ${numCameras} cameras`);
  }

  /**
   * Convert an instance type string to an EC2.InstanceSize enum
   * @param instanceType The instance type string (e.g., 't3.medium')
   * @returns The corresponding EC2.InstanceSize enum value
   */
  public static getInstanceSize(instanceType: string): ec2.InstanceSize {
    const size = instanceType.split('.')[1].toUpperCase();
    return ec2.InstanceSize[size as keyof typeof ec2.InstanceSize];
  }

  /**
   * Get the recommended instance type for the current number of cameras
   * @returns The recommended instance type
   */
  public static getRecommendedInstanceType(): string {
    const totalCameras = this.calculateTotalCameras();
    return this.calculateInstanceType(totalCameras);
  }

  /**
   * Get the EC2 instance type for the current number of cameras
   * @returns The EC2 instance type
   */
  public static getEc2InstanceType(): ec2.InstanceType {
    const instanceType = this.getRecommendedInstanceType();
    return ec2.InstanceType.of(
      ec2.InstanceClass.T3,
      this.getInstanceSize(instanceType)
    );
  }
} 