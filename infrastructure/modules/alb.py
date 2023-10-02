from collections.abc import Sequence
from dataclasses import dataclass

import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx


@dataclass
class ALBArgs:
    vpc_id: pulumi.Input[str]
    target_port: pulumi.Input[int]
    subnet_ids: pulumi.Input[Sequence[pulumi.Input[str]]]


class ALB(pulumi.ComponentResource):
    @property
    def target_group(self) -> pulumi.Output[aws.lb.TargetGroup]:
        return self._alb.default_target_group  # type: ignore[no-any-return]

    @property
    def dns_name(self) -> pulumi.Output[str]:
        return self._alb.load_balancer.dns_name  # type: ignore[no-any-return]

    def __init__(
        self, name: str, args: ALBArgs, opts: pulumi.ResourceOptions | None = None
    ):
        super().__init__("modules:alb:ALB", name, {}, opts)

        security_group = aws.ec2.SecurityGroup(
            name,
            vpc_id=args.vpc_id,
            ingress=[
                aws.ec2.SecurityGroupIngressArgs(
                    from_port=80,
                    to_port=80,
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

        self._alb = awsx.lb.ApplicationLoadBalancer(
            name,
            security_groups=[security_group.id],
            subnet_ids=args.subnet_ids,
            default_target_group_port=args.target_port,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs(
            {
                "security_group_id": security_group.id,
                "dns_name": self.dns_name,
            }
        )
