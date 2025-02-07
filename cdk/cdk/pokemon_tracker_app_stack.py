from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3 as s3,
    Stack,
)
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
            connection=ec2.Port.tcp(80),
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

        ec2_instance = ec2.Instance(
            self, 
            "pokemon_tracker_ec2_instance",
            instance_type=ec2.InstanceType("t2.nano"),
            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            role=iam_role,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=security_group,
            user_data=ec2.UserData.for_linux(),
        )
        self.ec2_instance = ec2_instance

        s3_bucket = s3.Bucket(
            self,
            "pokemon_tracker_s3_bucket",
            bucket_name="pokemon-tracker-s3-bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
        )
        self.s3_bucket = s3_bucket
        s3_bucket.grant_read(iam_role)