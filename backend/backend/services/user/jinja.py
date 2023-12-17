from typing import Any

from backend.i18 import translations
from backend.libs.templates.env import create_env

_env = create_env("backend.services.user")
_env.install_gettext_translations(translations)  # type: ignore[attr-defined]


def load_template(name: str, **kwargs: Any) -> str:
    template = _env.get_template(name)
    return template.render(**kwargs)
