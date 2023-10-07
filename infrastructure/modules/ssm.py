import pulumi
import pulumi_aws as aws


def create_ssm_parameter(
    name: str, value: pulumi.Input[str], parameter_type: str
) -> aws.ssm.Parameter:
    return aws.ssm.Parameter(name, type=parameter_type, value=value)
