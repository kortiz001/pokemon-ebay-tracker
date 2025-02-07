from aws_cdk import (
    aws_ec2 as ec2,
    Stack,
)
from constructs import Construct

class PokemonTrackerVpcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self, 
            "PokemonTrackerVpc",
            vpc_name="pokemon-tracker-vpc",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
            ],
            max_azs=1,
            cidr="100.0.0.0/16",
            nat_gateways=0
        )
        self.vpc = vpc