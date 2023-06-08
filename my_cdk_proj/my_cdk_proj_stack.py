import aws_cdk.aws_s3 as s3
from aws_cdk import Stack, Tags, aws_ecs_patterns, CfnOutput, aws_logs, pipelines, RemovalPolicy
from constructs import Construct
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_iam as iam
import aws_cdk.aws_ecs_patterns as ecs_patterns
import aws_cdk.aws_elasticloadbalancingv2 as elasticloadbalancing
import aws_cdk.aws_ec2 as ec2


class MyCdkProjStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.vpc_name = 'vpc-demo'
        self.vpc_cidr = '192.168.0.0/16'

        self.__create_vpc()


    #


    def __create_vpc(self):
        vpc_construct_id = 'vpc'


        self.vpc: ec2.Vpc = ec2.Vpc(
            self, vpc_construct_id,
            vpc_name=self.vpc_name,
            ip_addresses=ec2.IpAddresses.cidr(self.vpc_cidr),
            max_azs=3,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name='Public',
                    cidr_mask=20
                ), ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    name='Compute',
                    cidr_mask=20
                ), ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    name='RDS',
                    cidr_mask=20
                )
            ],
            nat_gateways=3,

        )

        CfnOutput(self, "Vpc-id", value=self.vpc.vpc_id, export_name="Vpc-id")
