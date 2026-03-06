#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.constants import REGION
from cdk.openclaw_stack import OpenClawStack

app = cdk.App()

OpenClawStack(
    app,
    'OpenClawStack',
    env=cdk.Environment(
        account=os.environ.get('CDK_DEFAULT_ACCOUNT'),
        region=REGION,
    ),
    termination_protection=True,
)

cdk.Tags.of(app).add('Project', 'OpenClaw')
cdk.Tags.of(app).add('ManagedBy', 'CDK')

app.synth()
