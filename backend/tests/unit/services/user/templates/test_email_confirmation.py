from backend.services.user.jinja import load_template


def test_email_confirmation() -> None:
    template = load_template("email-confirmation.html", link="http://test-link")

    assert (
        '<a href="http://test-link"\n        >Click here to confirm your email'
        "</a\n      >"
    ) in template
