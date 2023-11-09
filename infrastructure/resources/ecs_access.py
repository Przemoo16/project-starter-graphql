from pulumi_aws.ec2 import SecurityGroup

from resources.network import vpc_id

_security_group = SecurityGroup("ecs-access", vpc_id=vpc_id)

ecs_access_security_group_id = _security_group.id
