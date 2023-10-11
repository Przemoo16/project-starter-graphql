from collections.abc import Sequence
from dataclasses import dataclass

import pulumi
import pulumi_aws as aws


@dataclass
class ElastiCacheArgs:
    vpc_id: pulumi.Input[str]
    subnet_ids: pulumi.Input[Sequence[str]]
    port: pulumi.Input[int]
    description: pulumi.Input[str]
    engine_version: pulumi.Input[str]
    node_type: pulumi.Input[str]


class ElastiCache(pulumi.ComponentResource):
    @property
    def endpoint(self) -> pulumi.Output[str]:
        return self._cache.primary_endpoint_address  # type: ignore[no-any-return]

    def __init__(
        self,
        name: str,
        args: ElastiCacheArgs,
        opts: pulumi.ResourceOptions | None = None,
    ):
        super().__init__("modules:elasticache:ElastiCache", name, {}, opts)

        security_group = aws.ec2.SecurityGroup(
            name,
            vpc_id=args.vpc_id,
            ingress=[
                aws.ec2.SecurityGroupIngressArgs(
                    from_port=args.port,
                    to_port=args.port,
                    protocol="tcp",
                    cidr_blocks=["0.0.0.0/0"],
                )
            ],
            opts=pulumi.ResourceOptions(parent=self),
        )

        subnet_group = aws.elasticache.SubnetGroup(
            name,
            subnet_ids=args.subnet_ids,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self._cache = aws.elasticache.ReplicationGroup(
            name,
            port=args.port,
            description=args.description,
            engine_version=args.engine_version,
            node_type=args.node_type,
            security_group_ids=[security_group.id],
            subnet_group_name=subnet_group.name,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs(
            {
                "security_group_id": security_group.id,
                "subnet_group_name": subnet_group.name,
                "endpoint": self._cache.primary_endpoint_address,
            }
        )
