from pulumi import Config, Output
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

from resources.network import network_id, network_public_subnet_ids
from resources.services_access import services_access_security_group_id

_RESOURCE_NAME = "lb"

_config = Config()

_security_group = SecurityGroup(
    _RESOURCE_NAME,
    vpc_id=network_id,
    ingress=[
        SecurityGroupIngressArgs(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
        SecurityGroupIngressArgs(
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        ),
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
    vpc_id=network_id,
    health_check=TargetGroupHealthCheckArgs(
        path=_config.require("proxy_health_check_path")
    ),
)

_alb = ApplicationLoadBalancer(
    _RESOURCE_NAME,
    security_groups=[_security_group.id, services_access_security_group_id],
    subnet_ids=network_public_subnet_ids,
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

lb_dns_name: Output[str] = _alb.load_balancer.dns_name
