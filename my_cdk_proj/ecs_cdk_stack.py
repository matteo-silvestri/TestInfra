from aws_cdk import Stack, Tags, aws_ecs_patterns, CfnOutput, aws_logs, Fn
from constructs import Construct
import aws_cdk.aws_ecs as ecs
import aws_cdk.aws_iam as iam
import aws_cdk.aws_ecs_patterns as ecs_patterns
import aws_cdk.aws_elasticloadbalancingv2 as elasticloadbalancing
import aws_cdk.aws_ec2 as ec2
import aws_cdk as cdk


class EcsProjStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = vpc
        self.__create_ecs_fargate()
        self.__create_ecs_asg()


    def __create_ecs_asg(self):

        # Create Application Load Balancer
        security_group_al = ec2.SecurityGroup(self, "SG_ECS_EC2", vpc=self.vpc)
        security_group_al.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.all_traffic()
        )

        alb = elasticloadbalancing.ApplicationLoadBalancer(self, "ECS_EC2_ALB", security_group=security_group_al,
                                                           vpc=self.vpc, vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC),
                                                           internet_facing=True)
        target_group_http = elasticloadbalancing.ApplicationTargetGroup(self, "TargetGroup-ECS_EC2_ALB", port=80,
                                                                        vpc=self.vpc,
                                                                        protocol=elasticloadbalancing.ApplicationProtocol.HTTP,
                                                                        target_type=elasticloadbalancing.TargetType.IP)
        target_group_http.configure_health_check(protocol=elasticloadbalancing.Protocol.HTTP)

        listener_http = alb.add_listener("http-listener-ecs-ec2", open=True, port=80)

        # Create an ECS EC2 Servive cluster
        cluster = ecs.Cluster(self, "Cluster", vpc=self.vpc)

        autoscaling_gr = cluster.add_capacity("DefaultAutoScalingGroupCapacity",
                                              instance_type=ec2.InstanceType("t2.micro"),
                                              desired_capacity=3,
                                              vpc_subnets=ec2   .SubnetSelection(
                                                  subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)

                                              )
        autoscaling_gr.add_security_group(security_group_al)
        autoscaling_gr.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMFullAccess"))

        execution_role_ecs = iam.Role(self,
                                      "ecs-devops-execution-role-ecs",
                                      assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
                                      role_name="eecs-devops-execution-role-ecs")

        execution_role_ecs.add_to_policy(iam.PolicyStatement(effect=iam.Effect.ALLOW,
                                                             resources=["*"],
                                                             actions=["ecr:GetAuthorizationToken",
                                                                      "ecr:BatchCheckLayerAvailability",
                                                                      "ecr:GetDownloadUrlForLayer",
                                                                      "ecr:BatchGetImage",
                                                                      "logs:CreateLogStream",
                                                                      "logs:PutLogEvents",
                                                                      "SES:*"]))

        task_definition = ecs.Ec2TaskDefinition(self, "TaskDef", task_role=execution_role_ecs,
                                                network_mode=ecs.NetworkMode.AWS_VPC)

        container_ecs_ec2 = task_definition.add_container("DefaultContainer",
                                                          image=ecs.ContainerImage.from_registry(
                                                              "amazon/amazon-ecs-sample"),
                                                          memory_limit_mib=256,
                                                          port_mappings=[ecs.PortMapping(container_port=80)]
                                                          )

        security_ecs_ec2 = ec2.SecurityGroup(self, "ecs-sg-ec2", allow_all_outbound=True, vpc=self.vpc)
        security_ecs_ec2.add_egress_rule(security_group_al, connection=ec2.Port.all_traffic())
        # Instantiate an Amazon ECS Service
        service_ecs_ec2 = ecs.Ec2Service(self, "Service_EC2",
                                         cluster=cluster,
                                         task_definition=task_definition,
                                         security_groups=[security_ecs_ec2],
                                         )

        target_group_http.add_target(service_ecs_ec2)
        listener_http.add_target_groups("http-target-ecs-ec2", target_groups=[target_group_http])
    def __create_ecs_fargate(self):
        cluster = ecs.Cluster(
            self, 'EcsCluster',
            vpc=self.vpc
        )

        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            task_image_options={
                'image': ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")
            }
        )



        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(80),
            description="Allow http inbound from VPC"
        )
