from aws_cdk import (
    aws_ec2 as ec2,
    Stack,
)
from constructs import Construct

class PokemonTrackerAppStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, env, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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

        ec2_instance = ec2.Instance(
            self, 
            "pokemon_tracker_ec2_instance",
            instance_type=ec2.InstanceType("t2.nano"),
            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_23),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=security_group
        )
        self.ec2_instance = ec2_instance