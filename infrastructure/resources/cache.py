from pulumi import Config
from pulumi_aws.ec2 import (
    SecurityGroup,
    SecurityGroupEgressArgs,
    SecurityGroupIngressArgs,
)
from pulumi_aws.elasticache import ReplicationGroup, SubnetGroup

from resources.network import network_id, network_private_subnet_ids

_RESOURCE_NAME = "cache"

_config = Config()

_access_security_group = SecurityGroup(f"{_RESOURCE_NAME}-access", vpc_id=network_id)

_security_group = SecurityGroup(
    _RESOURCE_NAME,
    vpc_id=network_id,
    ingress=[
        SecurityGroupIngressArgs(
            from_port=_config.require_int("cache_port"),
            to_port=_config.require_int("cache_port"),
            protocol="tcp",
            security_groups=[_access_security_group.id],
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

_subnet_group = SubnetGroup(
    _RESOURCE_NAME,
    subnet_ids=network_private_subnet_ids,
)

_replication_group = ReplicationGroup(
    _RESOURCE_NAME,
    port=_config.require_int("cache_port"),
    description="Redis cache",
    engine_version=_config.require("cache_engine_version"),
    node_type=_config.require("cache_node_type"),
    security_group_ids=[_security_group.id],
    subnet_group_name=_subnet_group.name,
)

cache_access_security_group_id = _access_security_group.id
cache_endpoint = _replication_group.primary_endpoint_address
