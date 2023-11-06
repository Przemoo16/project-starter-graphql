from pulumi import Config
from pulumi_aws.ec2 import (
    SecurityGroup,
    SecurityGroupEgressArgs,
    SecurityGroupIngressArgs,
)
from pulumi_aws.lb import (
    ListenerDefaultActionArgs,
    TargetGroup,
    TargetGroupHealthCheckArgs,
)
from pulumi_awsx.lb import ApplicationLoadBalancer, ListenerArgs

from resources.network import vpc_id, vpc_public_subnet_ids

_RESOURCE_NAME = "lb"

_config = Config()

_security_group = SecurityGroup(
    _RESOURCE_NAME,
    vpc_id=vpc_id,
    ingress=[
        SecurityGroupIngressArgs(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
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

lb_target_group = TargetGroup(
    _RESOURCE_NAME,
    port=_config.require_int("proxy_container_port"),
    protocol="HTTP",
    target_type="ip",
    vpc_id=vpc_id,
    health_check=TargetGroupHealthCheckArgs(
        path=_config.require("proxy_health_check_path")
    ),
)

_alb = ApplicationLoadBalancer(
    _RESOURCE_NAME,
    security_groups=[_security_group.id],
    subnet_ids=vpc_public_subnet_ids,
    listener=ListenerArgs(
        port=80,
        protocol="HTTP",
        default_actions=[
            ListenerDefaultActionArgs(
                type="forward",
                target_group_arn=lb_target_group.arn,
            )
        ],
    ),
)

dns_name = _alb.load_balancer.dns_name
