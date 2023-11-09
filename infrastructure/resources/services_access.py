from pulumi_aws.ec2 import SecurityGroup

from resources.network import network_id

_security_group = SecurityGroup("services-access", vpc_id=network_id)

services_access_security_group_id = _security_group.id
