from pulumi import Config
from pulumi_aws.ec2 import (
    SecurityGroup,
    SecurityGroupEgressArgs,
    SecurityGroupIngressArgs,
)

from resources.network import network_id

_config = Config()

_worker_security_group = SecurityGroup(
    "worker",
    vpc_id=network_id,
    egress=[
        SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
)

_scheduler_security_group = SecurityGroup(
    "scheduler",
    vpc_id=network_id,
    egress=[
        SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
)

_backend_access_security_group = SecurityGroup("backend-access", vpc_id=network_id)
_backend_security_group = SecurityGroup(
    "backend",
    vpc_id=network_id,
    ingress=[
        SecurityGroupIngressArgs(
            from_port=_config.require_int("backend_container_port"),
            to_port=_config.require_int("backend_container_port"),
            protocol="tcp",
            security_groups=[_backend_access_security_group.id],
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

_frontend_access_security_group = SecurityGroup("frontend-access", vpc_id=network_id)
_frontend_security_group = SecurityGroup(
    "frontend",
    vpc_id=network_id,
    ingress=[
        SecurityGroupIngressArgs(
            from_port=_config.require_int("frontend_container_port"),
            to_port=_config.require_int("frontend_container_port"),
            protocol="tcp",
            security_groups=[_frontend_access_security_group.id],
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

_proxy_access_security_group = SecurityGroup("proxy-access", vpc_id=network_id)
_proxy_security_group = SecurityGroup(
    "proxy",
    vpc_id=network_id,
    ingress=[
        SecurityGroupIngressArgs(
            from_port=_config.require_int("proxy_container_port"),
            to_port=_config.require_int("proxy_container_port"),
            protocol="tcp",
            security_groups=[_proxy_access_security_group.id],
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

worker_security_group_id = _worker_security_group.id

scheduler_security_group_id = _scheduler_security_group.id

backend_access_security_group_id = _backend_access_security_group.id
backend_security_group_id = _backend_security_group.id

frontend_access_security_group_id = _frontend_access_security_group.id
frontend_security_group_id = _frontend_security_group.id

proxy_access_security_group_id = _proxy_access_security_group.id
proxy_security_group_id = _proxy_security_group.id
