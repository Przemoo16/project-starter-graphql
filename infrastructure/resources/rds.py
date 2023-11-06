from helpers.date import get_utc_timestamp
from helpers.hash import generate_hash
from pulumi import Config, ResourceOptions
from pulumi_aws.ec2 import SecurityGroup, SecurityGroupIngressArgs
from pulumi_aws.rds import Instance, SubnetGroup
from pulumi_aws.ssm import Parameter

from resources.network import vpc_id, vpc_private_subnet_ids

_RESOURCE_NAME = "database"

_config = Config()

_security_group = SecurityGroup(
    _RESOURCE_NAME,
    vpc_id=vpc_id,
    ingress=[
        SecurityGroupIngressArgs(
            from_port=_config.require_int("database_port"),
            to_port=_config.require_int("database_port"),
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
)

_subnet_group = SubnetGroup(
    _RESOURCE_NAME,
    subnet_ids=vpc_private_subnet_ids,
)

_database_username = Parameter(
    "database_username",
    type="SecureString",
    value=_config.require_secret("database_username"),
)
_database_password = Parameter(
    "database_password",
    type="SecureString",
    value=_config.require_secret("database_password"),
)

_instance = Instance(
    _RESOURCE_NAME,
    db_name=_config.require("database_name"),
    port=_config.require_int("database_port"),
    engine=_config.require("database_engine"),
    engine_version=_config.require("database_engine_version"),
    storage_type=_config.require("database_storage_type"),
    allocated_storage=_config.require_int("database_allocated_storage"),
    instance_class=_config.require("database_instance_class"),
    final_snapshot_identifier=(
        f"snapshot-{generate_hash(get_utc_timestamp(), digest_size=16)}"
    ),
    username=_database_username.value,
    password=_database_password.value,
    vpc_security_group_ids=[_security_group.id],
    db_subnet_group_name=_subnet_group.name,
    opts=ResourceOptions(ignore_changes=["final_snapshot_identifier"]),
)


database_name = _instance.db_name
database_host = _instance.address
database_port = _instance.port
database_endpoint = _instance.endpoint

database_username_parameter_name = _database_username.name
database_password_parameter_name = _database_password.name
