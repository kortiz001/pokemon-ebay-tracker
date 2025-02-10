from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_events as events,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_ssm as ssm,
    aws_events_targets as targets,
    Duration,
    Stack,
    Tags
)
import os
from pathlib import Path
from constructs import Construct

class PokemonTrackerS3UploadStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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

        s3_bucket = s3.Bucket.from_bucket_name(
            self,
            "pokemon_tracker_s3_bucket",
            bucket_name="pokemon-tracker-s3-bucket"
        )

        bucket_deployment = s3_deployment.BucketDeployment(
            self,
            "pokemon_tracker_s3_bucket_deployment",
            sources=[s3_deployment.Source.asset(f"{os.getenv('GITHUB_WORKSPACE')}/django")],
            destination_bucket=s3_bucket,
            destination_key_prefix="django",
            role=s3_deploy_role
        )
        self.bucket_deployment = bucket_deployment