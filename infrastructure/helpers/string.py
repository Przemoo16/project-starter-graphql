from pulumi import Input, Output


def create_image_name(repo_url: Input[str], image_tag: str) -> Output[str]:
    return Output.concat(repo_url, ":", image_tag)


def create_token_url_template(base_url: Input[str], path: str) -> Output[str]:
    return Output.concat(base_url, path, "?token={token}")


def create_url_from_namespace(url: Input[str], namespace: Input[str]) -> Output[str]:
    return Output.concat("http://", url, ".", namespace)
