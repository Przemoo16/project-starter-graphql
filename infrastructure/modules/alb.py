from collections.abc import Sequence
from dataclasses import dataclass

import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx


@dataclass
class ALBArgs:
    vpc_id: pulumi.Input[str]
    target_port: pulumi.Input[int]
    subnet_ids: pulumi.Input[Sequence[str]]
    health_check_path: pulumi.Input[str]


class ALB(pulumi.ComponentResource):
    @property
    def target_group(self) -> aws.lb.TargetGroup:
        return self._target_group

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

        self._target_group = aws.lb.TargetGroup(
            name,
            port=args.target_port,
            protocol="HTTP",
            target_type="ip",
            vpc_id=args.vpc_id,
            health_check=aws.lb.TargetGroupHealthCheckArgs(path=args.health_check_path),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self._alb = awsx.lb.ApplicationLoadBalancer(
            name,
            security_groups=[security_group.id],
            subnet_ids=args.subnet_ids,
            listener=awsx.lb.ListenerArgs(
                port=80,
                protocol="HTTP",
                default_actions=[
                    aws.lb.ListenerDefaultActionArgs(
                        type="forward",
                        target_group_arn=self._target_group.arn,
                    )
                ],
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs(
            {
                "security_group_id": security_group.id,
                "target_group_arn": self._target_group.arn,
                "dns_name": self._alb.load_balancer.dns_name,
            }
        )
