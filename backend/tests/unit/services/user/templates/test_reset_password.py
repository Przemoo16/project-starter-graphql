from backend.services.user.jinja import load_template


def test_reset_password() -> None:
    template = load_template("reset-password.html", link="http://test-link")

    assert (
        '<a href="http://test-link"\n        >Click here to reset your password'
        "</a\n      >"
    ) in template
