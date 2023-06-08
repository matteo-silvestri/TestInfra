from aws_cdk import Stack, Tags, aws_ecs_patterns, CfnOutput, aws_logs, Fn
from constructs import Construct
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_iam as iam
import aws_cdk.aws_ecs_patterns as ecs_patterns
import aws_cdk.aws_elasticloadbalancingv2 as elasticloadbalancing
import aws_cdk.aws_ec2 as ec2
import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_rds as rds


class StorageProjStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = vpc

        self.__create_s3()
        # self.__create_aurora()

    def __create_aurora(self):

        cluster = rds.DatabaseCluster(self, "Database",
                                      # multi_az=True,
                                      engine=rds.DatabaseClusterEngine.aurora_mysql(version=rds.AuroraMysqlEngineVersion.VER_2_08_1),
                                      credentials=rds.Credentials.from_generated_secret("clusteradmin"),
                                      # Optional - will default to 'admin' username and generated password
                                      instance_props=rds.InstanceProps(
                                          # optional , defaults to t3.medium
                                          instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2,
                                                                            ec2.InstanceSize.SMALL),
                                          vpc_subnets=ec2.SubnetSelection(
                                              subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                                          ),
                                          vpc=self.vpc
                                      )
                                      )

    def __create_s3(self):
        bucket1 = s3.Bucket(self, "sonar-bucket-one", bucket_name="test-bucket-sonar-one",
                            removal_policy=cdk.RemovalPolicy.DESTROY)
        # bucket1.add_to_resource_policy()
