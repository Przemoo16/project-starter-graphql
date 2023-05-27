import pulumi_awsx as awsx


def create_vpc(name: str) -> awsx.ec2.Vpc:
    return awsx.ec2.Vpc(name)
