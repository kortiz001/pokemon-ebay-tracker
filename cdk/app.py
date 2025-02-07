#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.vpc_stack import PokemonVpcStack
from cdk.pokemon_tracker_stack import PokemonTrackerStack


app = cdk.App()
PokemonVpcStack(
    app, 
    "pokemon-tracker-vpc-cdk",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

PokemonTrackerStack(
    app, 
    "pokemon-tracker-vpc-cdk",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()
