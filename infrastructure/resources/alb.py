import pulumi_aws as aws
import pulumi_awsx as awsx
from pulumi import Config

from resources.network import vpc_id, vpc_public_subnet_ids

_RESOURCE_NAME = "lb"

_config = Config()

_security_group = aws.ec2.SecurityGroup(
    _RESOURCE_NAME,
    vpc_id=vpc_id,
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
)

lb_target_group = aws.lb.TargetGroup(
    _RESOURCE_NAME,
    port=_config.require_int("proxy_container_port"),
    protocol="HTTP",
    target_type="ip",
    vpc_id=vpc_id,
    health_check=aws.lb.TargetGroupHealthCheckArgs(
        path=_config.require("proxy_health_check_path")
    ),
)

_lb = awsx.lb.ApplicationLoadBalancer(
    _RESOURCE_NAME,
    security_groups=[_security_group.id],
    subnet_ids=vpc_public_subnet_ids,
    listener=awsx.lb.ListenerArgs(
        port=80,
        protocol="HTTP",
        default_actions=[
            aws.lb.ListenerDefaultActionArgs(
                type="forward",
                target_group_arn=lb_target_group.arn,
            )
        ],
    ),
)

dns_name = _lb.load_balancer.dns_name
