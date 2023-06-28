from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

_env = Environment(
    loader=PackageLoader("backend.services.user"), autoescape=select_autoescape()
)


def load_template(name: str, **kwargs: Any) -> str:
    template = _env.get_template(name)
    return template.render(**kwargs)
