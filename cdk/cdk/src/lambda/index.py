import boto3
import os

def lambda_handler(event, context):
    ec2_client = boto3.client('ec2')
    
    # Retrieve instance ID from the CloudWatch event
    instance_id = event['detail']['EC2InstanceId']
    
    # Elastic IP to be attached
    allocation_id = os.getenv('ELASTIC_IP_ADDRESS_ALLOCATION_ID')
    
    # Attach Elastic IP to the new instance
    response = ec2_client.associate_address(
        InstanceId=instance_id,
        AllocationId=allocation_id
    )
    
    return response