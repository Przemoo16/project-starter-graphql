from pulumi_awsx.ec2 import Vpc

vpc = Vpc("main", enable_dns_hostnames=True)
