from pulumi_awsx.ec2 import Vpc

_vpc = Vpc("main", enable_dns_hostnames=True)

network_id = _vpc.vpc_id
network_public_subnet_ids = _vpc.public_subnet_ids
network_private_subnet_ids = _vpc.private_subnet_ids
