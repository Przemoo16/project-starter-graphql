import pulumi_awsx as awsx


def create_ecr_repository(name: str) -> awsx.ecr.Repository:
    return awsx.ecr.Repository(f"{name}-repository", name=name)
