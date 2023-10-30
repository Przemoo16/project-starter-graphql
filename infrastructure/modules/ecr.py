import pulumi_awsx as awsx


def create_ecr_repository(name: str) -> awsx.ecr.Repository:
    return awsx.ecr.Repository(
        name,
        lifecycle_policy=awsx.ecr.LifecyclePolicyArgs(
            rules=[
                awsx.ecr.LifecyclePolicyRuleArgs(
                    tag_status=awsx.ecr.LifecycleTagStatus.ANY,
                    description="Keep last 5 images",
                    maximum_number_of_images=5,
                ),
            ]
        ),
        force_delete=True,
    )
