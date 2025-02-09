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
    Stack,
    Tags
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
            instance_type=ec2.InstanceType("t3.nano"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            role=iam_role,
            security_group=security_group,
            user_data=user_data,
            launch_template_name="pokemon_tracker_ec2_lt",
            
        )
        Tags.of(ec2_lt).add('pokemon_ec2', 'true')
        self.ec2_lt = ec2_lt

        asg = autoscaling.AutoScalingGroup(
            self, 
            "pokemon_tracker_ec2_asg",
            auto_scaling_group_name="pokemon_tracker_ec2_asg",
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

        ssm_document_content = {
            "schemaVersion": "2.2",
            "description": "Copy Django files from S3 to EC2",
            "mainSteps": [
                {
                    "action": "aws:runShellScript",
                    "name": "copyAndUpdateDjangoFiles",
                    "inputs": {
                        "runCommand": [
                            "#!/bin/bash",
                            "echo \"Starting S3 copy to Django directory...\"",
                            "aws s3 cp s3://pokemon-tracker-s3-bucket/django/ /django/ --recursive",
                            "echo \"Django files copied successfully.\""
                        ]
                    }
                }
            ]
        }
        ssm_document = ssm.CfnDocument(
            self,
            "pokemon_tracker_ssm_document",
            name="pokemon_tracker_ssm_document",
            content=ssm_document_content,
            target_type="/AWS::EC2::Instance",
            document_type="Command"
        )
        self.ssm_document = ssm_document

        ssm_association = ssm.CfnAssociation(
            self,
            f"pokemon_tracker_ssm_association_{os.getenv('GITHUB_RUN_ID')}",
            name=ssm_document.name,
            targets=[ssm.CfnAssociation.TargetProperty(
                key="tag:pokemon_ec2",
                values=["true"]
            )],            
        )
        self.ssm_association = ssm_association

        elastic_ip = ec2.CfnEIP(
            self,
            "pokemon_tracker_elastic_ip",
            domain="vpc"
        )
        self.elastic_ip = elastic_ip

        iam_role_asg_eip = iam.Role(
            self,
            "pokemon_tracker_asg_eip_iam_role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            role_name="pokemon-tracker-asg_eip_iam-role",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"),
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole")
            ]
        )
        self.iam_role_asg_eip = iam_role_asg_eip
        iam_role_asg_eip.attach_inline_policy(iam.Policy(self, "attach-elastic-ip-policy",
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "ec2:AssignPrivateIpAddresses",
                        "ec2:AssociateAddress"
                    ],
                    resources=["*"],
                    effect=iam.Effect.ALLOW
                )
            ]
        ))

        lambda_file_path = str(current_file.parent / "src" / "lambda")
        asg_eip_lambda = lambda_.Function(
            self,
            "pokemon_tracker_asg_eip_lambda",
            function_name="pokemon_tracker_asg_eip_lambda",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="index.lambda_handler",
            code=lambda_.Code.from_asset(lambda_file_path),
            environment={
                "ELASTIC_IP_ADDRESS_ALLOCATION_ID": elastic_ip.attr_allocation_id
            },
            role=iam_role_asg_eip
        )
        self.asg_eip_lambda = asg_eip_lambda

        asg_eip_rule = events.Rule(
            self, 
            "pokemon_tracker_asg_eip_event_rule",
            rule_name="pokemon_tracker_asg_eip_event_rule",
            event_pattern=events.EventPattern(
                source=["aws.autoscaling"],
                detail_type=["EC2 Instance-launch Lifecycle Action"]
            )
        )

        asg_eip_lambda.add_permission(
            "pokemon_tracker_asg_eip_lambda_permission",
            principal=iam.ServicePrincipal("events.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn=asg_eip_rule.rule_arn
        )

        asg_eip_rule.add_target(targets.LambdaFunction(asg_eip_lambda))