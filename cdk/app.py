#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.pokemon_tracker_vpc_stack import PokemonTrackerVpcStack
from cdk.cdk.pokemon_tracker_s3_upload_stack import PokemonTrackerS3UploadStack
from cdk.cdk.pokemon_tracker_app_stack import PokemonTrackerAppStack

app = cdk.App()
pokemon_tracker_vpc_stack = PokemonTrackerVpcStack(
    app, 
    "pokemon-tracker-vpc-cdk",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

pokemon_tracker_s3_upload_stack = PokemonTrackerS3UploadStack(
    app, 
    "pokemon-tracker-s3-upload-cdk",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

pokemon_tracker_app = PokemonTrackerAppStack(
    app, 
    "pokemon-tracker-app-cdk",
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)
pokemon_tracker_app.add_dependency(pokemon_tracker_s3_upload_stack)

app.synth()
