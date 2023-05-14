import pulumi
import pulumi_awsx as awsx

vpc = awsx.ec2.Vpc("vpc")

pulumi.export("vpc_id", vpc.vpc_id)
pulumi.export("private_subnets_ids", vpc.private_subnet_ids)
pulumi.export("public_subnets_ids", vpc.public_subnet_ids)
