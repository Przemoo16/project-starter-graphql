import pulumi


def create_redis_url(uri: pulumi.Input[str]) -> pulumi.Output[str]:
    return pulumi.Output.concat("redis://", uri)


def create_image_name(
    repo_url: pulumi.Input[str], image_tag: str
) -> pulumi.Output[str]:
    return pulumi.Output.concat(repo_url, ":", image_tag)


def create_token_url_template(
    base_url: pulumi.Input[str], path: str
) -> pulumi.Output[str]:
    return pulumi.Output.concat(base_url, path, "?token={token}")


def create_upstream(
    url: pulumi.Input[str], namespace: pulumi.Input[str]
) -> pulumi.Output[str]:
    return pulumi.Output.concat("http://", url, ".", namespace)
