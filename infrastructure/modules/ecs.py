from collections.abc import Mapping, Sequence
from dataclasses import dataclass

import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx


@dataclass
class ECSServiceArgs:
    cluster_arn: pulumi.Input[str]
    vpc_id: pulumi.Input[str]
    dns_namespace_id: pulumi.Input[str]
    subnet_ids: pulumi.Input[Sequence[str]]
    service_desired_count: pulumi.Input[int]
    task_cpu: pulumi.Input[str]
    task_memory: pulumi.Input[str]
    task_role_arn: pulumi.Input[str]
    execution_role_arn: pulumi.Input[str]
    container_image: pulumi.Input[str]
    container_port: pulumi.Input[int]
    target_group: pulumi.Input[aws.lb.TargetGroup] | None = None
    container_command: pulumi.Input[Sequence[str]] | None = None
    container_environment: Mapping[str, pulumi.Input[str]] | None = None
    container_secrets: Mapping[str, pulumi.Input[str]] | None = None


class ECSService(pulumi.ComponentResource):
    @property
    def service_discovery_name(self) -> pulumi.Output[str]:
        return self._service_discovery_service.name  # type: ignore[no-any-return]

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

        self._service_discovery_service = aws.servicediscovery.Service(
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
                registry_arn=self._service_discovery_service.arn, container_name=name
            ),
            network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
                subnets=args.subnet_ids,
                security_groups=[security_group.id],
            ),
            desired_count=args.service_desired_count,
            task_definition_args=awsx.ecs.FargateServiceTaskDefinitionArgs(
                cpu=args.task_cpu,
                memory=args.task_memory,
                task_role=awsx.awsx.DefaultRoleWithPolicyArgs(
                    role_arn=args.task_role_arn
                ),
                execution_role=awsx.awsx.DefaultRoleWithPolicyArgs(
                    role_arn=args.execution_role_arn
                ),
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
                    secrets=_convert_container_secrets(args.container_secrets),
                ),
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs(
            {
                "security_group_id": security_group.id,
                "service_discovery_service_name": self._service_discovery_service.name,
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


def _convert_container_secrets(
    secrets: Mapping[str, pulumi.Input[str]] | None
) -> list[awsx.ecs.TaskDefinitionSecretArgs] | None:
    if not secrets:
        return None
    return [
        awsx.ecs.TaskDefinitionSecretArgs(name=name, value_from=value_from)
        for name, value_from in secrets.items()
    ]
