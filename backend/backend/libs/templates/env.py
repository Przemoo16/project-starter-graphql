from jinja2 import Environment, PackageLoader, select_autoescape


def create_env(package_name: str) -> Environment:
    return Environment(
        loader=PackageLoader(package_name),
        autoescape=select_autoescape(),
        extensions=["jinja2.ext.i18n"],
    )
