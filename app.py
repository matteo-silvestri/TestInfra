#!/usr/bin/env python3
import os

import aws_cdk as cdk

from my_cdk_proj.ecs_cdk_stack import EcsProjStack
from my_cdk_proj.my_cdk_proj_stack import MyCdkProjStack
from my_cdk_proj.storage_cdk_stack import StorageProjStack

app = cdk.App()
stack_vpc = MyCdkProjStack(app, "MyCdkProjStack",

                           env=cdk.Environment(account="AccountId", region="us-east-1"),

                           )

stack_ecs = EcsProjStack(app, "EcsProjStack",
                         env=cdk.Environment(account="AccountId", region="us-east-1"),
                         vpc=stack_vpc.vpc
                         )

stack_storage = StorageProjStack(app, "StorageProjStack",
                                 env=cdk.Environment(account="AccountId", region="us-east-1"),
                                 vpc=stack_vpc.vpc

                                 )

app.synth()
