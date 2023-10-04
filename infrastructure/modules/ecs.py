from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx


def create_ecs_cluster(name: str) -> aws.ecs.Cluster:
    return aws.ecs.Cluster(name)


def create_private_dns_namespace(
    name: str,
    vpc_id: pulumi.Input[str],
) -> aws.servicediscovery.PrivateDnsNamespace:
    return aws.servicediscovery.PrivateDnsNamespace(name, vpc=vpc_id)


@dataclass
class ECSServiceArgs:
    cluster_arn: pulumi.Input[str]
    vpc_id: pulumi.Input[str]
    dns_namespace_id: pulumi.Input[str]
    subnet_ids: pulumi.Input[Sequence[pulumi.Input[str]]]
    service_desired_count: pulumi.Input[int]
    task_cpu: pulumi.Input[str]
    task_memory: pulumi.Input[str]
    container_image: pulumi.Input[str]
    container_port: pulumi.Input[int]
    target_group: pulumi.Input[aws.lb.TargetGroup] | None = None
    container_command: pulumi.Input[Sequence[pulumi.Input[str]]] | None = None
    container_environment: Mapping[str, pulumi.Input[str]] | None = None


class ECSService(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        args: ECSServiceArgs,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("modules:ecs:ECSService", name, {}, opts)

        security_group = aws.ec2.SecurityGroup(
            name,
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

        service_discovery_service = aws.servicediscovery.Service(
            name,
            dns_config=aws.servicediscovery.ServiceDnsConfigArgs(
                namespace_id=args.dns_namespace_id,
                dns_records=[
                    aws.servicediscovery.ServiceDnsConfigDnsRecordArgs(
                        ttl=10,
                        type="A",
                    )
                ],
                routing_policy="MULTIVALUE",
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        awsx.ecs.FargateService(
            name,
            cluster=args.cluster_arn,
            service_registries=aws.ecs.ServiceServiceRegistriesArgs(
                registry_arn=service_discovery_service.arn, container_name=name
            ),
            network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
                subnets=args.subnet_ids,
                security_groups=[security_group.id],
            ),
            desired_count=args.service_desired_count,
            task_definition_args=awsx.ecs.FargateServiceTaskDefinitionArgs(
                cpu=args.task_cpu,
                memory=args.task_memory,
                container=awsx.ecs.TaskDefinitionContainerDefinitionArgs(
                    name=name,
                    image=args.container_image,
                    essential=True,
                    port_mappings=_get_port_mappings(
                        args.target_group, args.container_port
                    ),
                    command=args.container_command,
                    environment=_convert_container_environment(
                        args.container_environment
                    ),
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs(
            {
                "security_group_id": security_group.id,
                "service_discovery_service_arn": service_discovery_service.arn,
            }
        )


def _get_port_mappings(
    target_group: pulumi.Input[aws.lb.TargetGroup] | None,
    container_port: pulumi.Input[int],
) -> list[awsx.ecs.TaskDefinitionPortMappingArgs]:
    return [
        awsx.ecs.TaskDefinitionPortMappingArgs(
            target_group=target_group,
            container_port=None if target_group else container_port,
        )
    ]


def _convert_container_environment(
    environment: Mapping[str, pulumi.Input[str]] | None
) -> list[awsx.ecs.TaskDefinitionKeyValuePairArgs] | None:
    if not environment:
        return None
    return [
        awsx.ecs.TaskDefinitionKeyValuePairArgs(name=name, value=value)
        for name, value in environment.items()
    ]
