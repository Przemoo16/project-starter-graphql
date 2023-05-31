from collections.abc import Sequence
from dataclasses import dataclass

import pulumi
import pulumi_aws as aws


@dataclass
class RDSArgs:
    vpc_id: pulumi.Input[str]
    subnet_ids: pulumi.Input[Sequence[pulumi.Input[str]]]
    name: pulumi.Input[str]
    port: pulumi.Input[int]
    engine: pulumi.Input[str]
    engine_version: pulumi.Input[str]
    storage_type: pulumi.Input[str]
    allocated_storage: pulumi.Input[int]
    instance_class: pulumi.Input[str]
    final_snapshot_identifier: pulumi.Input[str]
    username: pulumi.Input[str]
    password: pulumi.Input[str]


class RDS(pulumi.ComponentResource):
    @property
    def username(self) -> pulumi.Output[str]:
        return self._database.username  # type: ignore[no-any-return]

    @property
    def name(self) -> pulumi.Output[str]:
        return self._database.name  # type: ignore[no-any-return]

    @property
    def host(self) -> pulumi.Output[str]:
        return self._database.address  # type: ignore[no-any-return]

    @property
    def port(self) -> pulumi.Output[int]:
        return self._database.port  # type: ignore[no-any-return]

    @property
    def endpoint(self) -> pulumi.Output[str]:
        return self._database.endpoint  # type: ignore[no-any-return]

    def __init__(
        self, name: str, args: RDSArgs, opts: pulumi.ResourceOptions | None = None
    ):
        super().__init__("modules:rds:RDS", name, {}, opts)

        security_group = aws.ec2.SecurityGroup(
            f"{name}-security-group",
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

        subnet_group = aws.rds.SubnetGroup(
            f"{name}-subnet-group",
            subnet_ids=args.subnet_ids,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self._database = aws.rds.Instance(
            f"{name}-instance",
            name=args.name,
            port=args.port,
            engine=args.engine,
            engine_version=args.engine_version,
            storage_type=args.storage_type,
            allocated_storage=args.allocated_storage,
            instance_class=args.instance_class,
            final_snapshot_identifier=args.final_snapshot_identifier,
            username=args.username,
            password=args.password,
            vpc_security_group_ids=[security_group.id],
            db_subnet_group_name=subnet_group.name,
            opts=pulumi.ResourceOptions(
                parent=self, ignore_changes=["final_snapshot_identifier"]
            ),
        )

        self.register_outputs(
            {
                "security_group_id": security_group.id,
                "subnet_group_id": subnet_group.id,
                "username": self.username,
                "name": self.name,
                "host": self.host,
                "port": self.port,
                "endpoint": self.endpoint,
            }
        )