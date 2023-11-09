from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from pulumi import Input, ResourceOptions
from pulumi_aws.ec2 import (
    SecurityGroup,
    SecurityGroupEgressArgs,
    SecurityGroupIngressArgs,
)
from pulumi_aws.ecs import ServiceNetworkConfigurationArgs, ServiceServiceRegistriesArgs
from pulumi_aws.lb import TargetGroup
from pulumi_aws.servicediscovery import (
    Service,
    ServiceDnsConfigArgs,
    ServiceDnsConfigDnsRecordArgs,
)
from pulumi_awsx.awsx import DefaultRoleWithPolicyArgs
from pulumi_awsx.ecs import (
    FargateService,
    FargateServiceTaskDefinitionArgs,
    TaskDefinitionContainerDefinitionArgs,
    TaskDefinitionKeyValuePairArgs,
    TaskDefinitionPortMappingArgs,
    TaskDefinitionSecretArgs,
)


@dataclass
class NetworkConfig:
    vpc_id: Input[str]
    subnet_ids: Input[Sequence[str]]
    ingress_security_groups_ids: Sequence[Input[str]]
    dns_namespace_id: Input[str]
    security_groups_ids: Sequence[Input[str]] | None = None


@dataclass
class ServiceConfig:
    cluster_arn: Input[str]
    desired_count: Input[int]


@dataclass
class TaskConfig:
    cpu: Input[str]
    memory: Input[str]
    task_role_arn: Input[str]
    execution_role_arn: Input[str]


@dataclass
class ContainerConfig:
    image: Input[str]
    port: Input[int]
    target_group: Input[TargetGroup] | None = None
    command: Input[Sequence[str]] | None = None
    environment: Mapping[str, Input[str]] | None = None
    secrets: Mapping[str, Input[str]] | None = None


@dataclass
class _ECSService:
    service_discovery_name: str
    fargate_service: FargateService


def create_ecs_service(  # pylint: disable=too-many-arguments
    name: str,
    network: NetworkConfig,
    service: ServiceConfig,
    task: TaskConfig,
    container: ContainerConfig,
    service_opts: ResourceOptions | None = None,
) -> _ECSService:
    security_group = SecurityGroup(
        name,
        vpc_id=network.vpc_id,
        ingress=[
            SecurityGroupIngressArgs(
                from_port=container.port,
                to_port=container.port,
                protocol="tcp",
                security_groups=network.ingress_security_groups_ids,
            )
        ],
        egress=[
            SecurityGroupEgressArgs(
                from_port=0,
                to_port=0,
                protocol="-1",
                cidr_blocks=["0.0.0.0/0"],
            )
        ],
    )

    service_discovery_service = Service(
        name,
        dns_config=ServiceDnsConfigArgs(
            namespace_id=network.dns_namespace_id,
            dns_records=[
                ServiceDnsConfigDnsRecordArgs(
                    ttl=10,
                    type="A",
                )
            ],
            routing_policy="MULTIVALUE",
        ),
    )

    fargate_service = FargateService(
        name,
        cluster=service.cluster_arn,
        service_registries=ServiceServiceRegistriesArgs(
            registry_arn=service_discovery_service.arn, container_name=name
        ),
        network_configuration=ServiceNetworkConfigurationArgs(
            subnets=network.subnet_ids,
            security_groups=[security_group.id, *(network.security_groups_ids or [])],
        ),
        desired_count=service.desired_count,
        task_definition_args=FargateServiceTaskDefinitionArgs(
            cpu=task.cpu,
            memory=task.memory,
            task_role=DefaultRoleWithPolicyArgs(role_arn=task.task_role_arn),
            execution_role=DefaultRoleWithPolicyArgs(role_arn=task.execution_role_arn),
            container=TaskDefinitionContainerDefinitionArgs(
                name=name,
                image=container.image,
                essential=True,
                port_mappings=_get_port_mappings(
                    container.target_group, container.port
                ),
                command=container.command,
                environment=_convert_container_environment(container.environment),
                secrets=_convert_container_secrets(container.secrets),
            ),
        ),
        opts=service_opts,
    )

    return _ECSService(
        service_discovery_name=service_discovery_service.name,
        fargate_service=fargate_service,
    )


def _get_port_mappings(
    target_group: Input[TargetGroup] | None,
    container_port: Input[int],
) -> list[TaskDefinitionPortMappingArgs]:
    return [
        TaskDefinitionPortMappingArgs(
            target_group=target_group,
            container_port=None if target_group else container_port,
        )
    ]


def _convert_container_environment(
    environment: Mapping[str, Input[str]] | None
) -> list[TaskDefinitionKeyValuePairArgs] | None:
    if not environment:
        return None
    return [
        TaskDefinitionKeyValuePairArgs(name=name, value=value)
        for name, value in environment.items()
    ]


def _convert_container_secrets(
    secrets: Mapping[str, Input[str]] | None
) -> list[TaskDefinitionSecretArgs] | None:
    if not secrets:
        return None
    return [
        TaskDefinitionSecretArgs(name=name, value_from=value_from)
        for name, value_from in secrets.items()
    ]
