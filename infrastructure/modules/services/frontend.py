import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx
from modules.alb import alb
from modules.ecs import cluster
from modules.network import vpc

config = pulumi.Config()

frontend_security_group = aws.ec2.SecurityGroup(
    "frontend-security-group",
    vpc_id=vpc.vpc_id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=config.require_int("frontend_container_port"),
            to_port=config.require_int("frontend_container_port"),
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
)


frontend_service = awsx.ecs.FargateService(
    "frontend-service",
    cluster=cluster.arn,
    network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
        subnets=vpc.private_subnet_ids, security_groups=[frontend_security_group.id]
    ),
    desired_count=config.require_int("frontend_service_desired_count"),
    task_definition_args=awsx.ecs.FargateServiceTaskDefinitionArgs(
        cpu=config.require("frontend_task_cpu"),
        memory=config.require("frontend_task_memory"),
        container=awsx.ecs.TaskDefinitionContainerDefinitionArgs(
            image=config.require("frontend_container_image"),
            essential=True,
            port_mappings=[
                awsx.ecs.TaskDefinitionPortMappingArgs(
                    target_group=alb.default_target_group
                )
            ],
        ),
    ),
)

pulumi.export("frontend_security_group_id", frontend_security_group.id)
