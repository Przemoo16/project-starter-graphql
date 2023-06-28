from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

from backend.i18 import translations

_env = Environment(
    loader=PackageLoader("backend.services.user"),
    autoescape=select_autoescape(),
    extensions=["jinja2.ext.i18n"],
)
# pylint: disable=no-member
_env.install_gettext_translations(translations)  # type: ignore[attr-defined]


def load_template(name: str, **kwargs: Any) -> str:
    template = _env.get_template(name)
    return template.render(**kwargs)
