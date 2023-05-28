from collections.abc import Sequence
from dataclasses import dataclass

import pulumi
import pulumi_aws as aws


@dataclass
class RDSArgs:
    vpc_id: pulumi.Input[str]
    subnet_ids: pulumi.Input[Sequence[str]]
    port: pulumi.Input[int]
    name: pulumi.Input[str]
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
            # TODO: Check if egress is needed
            # egress=[
            #     aws.ec2.SecurityGroupEgressArgs(
            #         from_port=0,
            #         to_port=0,
            #         protocol="-1",
            #         cidr_blocks=["0.0.0.0/0"],
            #     )
            # ],
            opts=pulumi.ResourceOptions(parent=self),
        )

        subnet_group = aws.rds.SubnetGroup(
            f"{name}-subnet-group",
            subnet_ids=args.subnet_ids,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self._database = aws.rds.Instance(
            f"{name}-rds",
            name=args.name,
            engine=args.engine,
            engine_version=args.engine_version,
            storage_type=args.storage_type,
            allocated_storage=args.allocated_storage,
            instance_class=args.instance_class,
            final_snapshot_identifier=args.final_snapshot_identifier,
            username=args.username,
            password=args.password,
            db_subnet_group_name=subnet_group.id,
            vpc_security_group_ids=[security_group.id],
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs(
            {
                "security_group_id": security_group.id,
                "subnet_group_id": subnet_group.id,
                "username": self._database.username,
                "name": self._database.name,
                "host": self._database.address,
                "port": self._database.port,
                "endpoint": self.endpoint,
            }
        )
