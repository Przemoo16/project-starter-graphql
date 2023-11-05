from pulumi import Config
from pulumi_aws.ec2 import SecurityGroup, SecurityGroupIngressArgs
from pulumi_aws.elasticache import ReplicationGroup, SubnetGroup

from resources.network import vpc_id, vpc_private_subnet_ids

_RESOURCE_NAME = "cache"

_config = Config()

_security_group = SecurityGroup(
    _RESOURCE_NAME,
    vpc_id=vpc_id,
    ingress=[
        SecurityGroupIngressArgs(
            from_port=_config.require_int("cache_port"),
            to_port=_config.require_int("cache_port"),
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
)

_subnet_group = SubnetGroup(
    _RESOURCE_NAME,
    subnet_ids=vpc_private_subnet_ids,
)

_cache = ReplicationGroup(
    _RESOURCE_NAME,
    port=_config.require_int("cache_port"),
    description="Redis cache",
    engine_version=_config.require("cache_engine_version"),
    node_type=_config.require("cache_node_type"),
    security_group_ids=[_security_group.id],
    subnet_group_name=_subnet_group.name,
)

cache_endpoint = _cache.primary_endpoint_address
