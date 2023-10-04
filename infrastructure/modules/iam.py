import pulumi
import pulumi_aws as aws


def create_role(name: str, assume_role_policy: str) -> aws.iam.Role:
    return aws.iam.Role(name, assume_role_policy=assume_role_policy)


def create_policy(name: str, policy: str) -> aws.iam.Policy:
    return aws.iam.Policy(name, policy=policy)


def create_role_policy_attachment(
    name: str, role_name: pulumi.Input[str], policy_arn: pulumi.Input[str]
) -> aws.iam.RolePolicyAttachment:
    return aws.iam.RolePolicyAttachment(name, role=role_name, policy_arn=policy_arn)
