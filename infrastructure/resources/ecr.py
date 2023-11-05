from pulumi_awsx.ecr import (
    LifecyclePolicyArgs,
    LifecyclePolicyRuleArgs,
    LifecycleTagStatus,
    Repository,
)


def _create_ecr_repository(name: str) -> Repository:
    return Repository(
        name,
        lifecycle_policy=LifecyclePolicyArgs(
            rules=[
                LifecyclePolicyRuleArgs(
                    tag_status=LifecycleTagStatus.ANY,
                    description="Keep last 5 images",
                    maximum_number_of_images=5,
                ),
            ]
        ),
        force_delete=True,
    )


_frontend_repository = _create_ecr_repository("frontend")
_backend_repository = _create_ecr_repository("backend")
_proxy_repository = _create_ecr_repository("proxy")

frontend_repository_url = _frontend_repository.url
backend_repository_url = _backend_repository.url
proxy_repository_url = _proxy_repository.url
