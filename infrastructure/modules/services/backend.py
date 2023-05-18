import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx
from modules.ecs import cluster
from modules.network import vpc

config = pulumi.Config()

backend_security_group = aws.ec2.SecurityGroup(
    "backend-security-group",
    vpc_id=vpc.vpc_id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=config.require_int("backend_container_port"),
            to_port=config.require_int("backend_container_port"),
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

backend_service = awsx.ecs.FargateService(
    "backend-service",
    cluster=cluster.arn,
    network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
        subnets=vpc.private_subnet_ids, security_groups=[backend_security_group.id]
    ),
    desired_count=config.require_int("backend_service_desired_count"),
    task_definition_args=awsx.ecs.FargateServiceTaskDefinitionArgs(
        cpu=config.require("backend_task_cpu"),
        memory=config.require("backend_task_memory"),
        container=awsx.ecs.TaskDefinitionContainerDefinitionArgs(
            image=config.require("backend_container_image"),
            essential=True,
            port_mappings=[
                awsx.ecs.TaskDefinitionPortMappingArgs(
                    container_port=config.require_int("backend_container_port")
                )
            ],
        ),
    ),
)

pulumi.export("backend_security_group_id", backend_security_group.id)
