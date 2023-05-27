from collections.abc import Sequence
from dataclasses import dataclass

import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx


def create_ecs_cluster(name: str) -> aws.ecs.Cluster:
    return aws.ecs.Cluster(name)


@dataclass
class ECSServiceArgs:
    cluster_arn: pulumi.Input[str]
    vpc_id: pulumi.Input[str]
    subnet_ids: pulumi.Input[Sequence[str]]
    service_desired_count: pulumi.Input[int]
    task_cpu: pulumi.Input[str]
    task_memory: pulumi.Input[str]
    container_image: pulumi.Input[str]
    container_port: pulumi.Input[int]
    target_group: pulumi.Input[aws.lb.TargetGroup] | None = None


class ECSService(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        args: ECSServiceArgs,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("modules:ecs:ECSService", name, {}, opts)

        security_group = aws.ec2.SecurityGroup(
            f"{name}-security-group",
            vpc_id=args.vpc_id,
            ingress=[
                aws.ec2.SecurityGroupIngressArgs(
                    from_port=args.container_port,
                    to_port=args.container_port,
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
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.service = awsx.ecs.FargateService(
            f"{name}-service",
            cluster=args.cluster_arn,
            network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
                subnets=args.subnet_ids,
                security_groups=[security_group.id],
            ),
            desired_count=args.service_desired_count,
            task_definition_args=awsx.ecs.FargateServiceTaskDefinitionArgs(
                cpu=args.task_cpu,
                memory=args.task_memory,
                container=awsx.ecs.TaskDefinitionContainerDefinitionArgs(
                    image=args.container_image,
                    essential=True,
                    port_mappings=[
                        awsx.ecs.TaskDefinitionPortMappingArgs(
                            target_group=args.target_group,
                            container_port=None
                            if args.target_group
                            else args.container_port,
                        )
                    ],
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs(
            {
                "security_group_id": security_group.id,
            }
        )
