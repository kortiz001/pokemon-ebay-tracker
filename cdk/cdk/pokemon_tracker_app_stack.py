from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    Stack,
)
import os
from pathlib import Path
from constructs import Construct

class PokemonTrackerAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc.from_lookup(
            self,
            "pokemon_tracker_vpc", 
            vpc_name="pokemon-tracker-vpc" 
        )

        security_group = ec2.SecurityGroup(
            self,
            "pokemon_tracker_security_group",
            vpc=vpc
        )
        self.security_group = security_group

        security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("0.0.0.0/0"),
            connection=ec2.Port.tcp(8000),
            description="Allow HTTP"
        )

        iam_role = iam.Role(
            self,
            "pokemon_tracker_iam_role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            role_name="pokemon-tracker-iam-role",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
            ]
        )
        self.iam_role = iam_role

        user_data = ec2.UserData.for_linux()

        current_file = Path(__file__).resolve()
        user_data_file = current_file.parent / "src" / "user_data.txt"

        with open(str(user_data_file), "r") as f:
            user_data.add_commands(f.read())

        ec2_lt = ec2.LaunchTemplate(
            self,
            "pokemon_tracker_ec2_lt",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            role=iam_role,
            security_group=security_group,
            user_data=user_data,
            spot_options=ec2.LaunchTemplateSpotOptions(
                max_price=0.01,
            ),
            launch_template_name="pokemon_tracker_ec2_lt",
        )
        self.ec2_lt = ec2_lt

        asg = autoscaling.AutoScalingGroup(
            self, 
            "pokemon_tracker_ec2_asg",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            launch_template=ec2_lt,
            min_capacity=1,
            max_capacity=1,
        )
        self.asg = asg

        s3_bucket = s3.Bucket(
            self,
            "pokemon_tracker_s3_bucket",
            bucket_name="pokemon-tracker-s3-bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )
        self.s3_bucket = s3_bucket
        s3_bucket.grant_read(iam_role)

        s3_deploy_role = iam.Role(
            self,
            "pokemon_tracker_s3_deploy_role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="pokemon-tracker-s3-deploy-role",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess")
            ]
        )
        self.s3_deploy_role = s3_deploy_role

        s3_deployment.BucketDeployment(
            self,
            "pokemon_tracker_s3_bucket_deployment",
            sources=[s3_deployment.Source.asset(f"{os.getenv('GITHUB_WORKSPACE')}/django")],
            destination_bucket=s3_bucket,
            destination_key_prefix="django",
            role=s3_deploy_role
        )