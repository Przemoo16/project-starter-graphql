import pulumi


def create_redis_url(uri: pulumi.Output[str]) -> pulumi.Output[str]:
    return pulumi.Output.concat("redis://", uri)


def create_image_name(
    repo_url: pulumi.Output[str], image_tag: str
) -> pulumi.Output[str]:
    return pulumi.Output.concat(repo_url, ":", image_tag)
