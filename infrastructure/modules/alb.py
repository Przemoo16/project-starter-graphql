import pulumi
import pulumi_aws as aws
import pulumi_awsx as awsx
from modules.network import vpc

config = pulumi.Config()

alb_security_group = aws.ec2.SecurityGroup(
    "alb-security-group",
    vpc_id=vpc.vpc_id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
)

alb = awsx.lb.ApplicationLoadBalancer(
    "alb",
    security_groups=[alb_security_group.id],
    subnet_ids=vpc.public_subnet_ids,
    default_target_group_port=config.require_int("frontend_container_port"),
)

pulumi.export("alb_security_group_id", alb_security_group.id)
pulumi.export("alb_dns_name", alb.load_balancer.dns_name)
