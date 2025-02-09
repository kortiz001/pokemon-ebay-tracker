#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.pokemon_tracker_vpc_stack import PokemonTrackerVpcStack
from cdk.cdk.pokemon_tracker_app_stack import PokemonTrackerAppStack


app = cdk.App()
pokemon_tracker_vpc_stack = PokemonTrackerVpcStack(
    app, 
    "pokemon-tracker-vpc-cdk",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

PokemonTrackerAppStack(
    app, 
    "pokemon-tracker-app-cdk",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()
