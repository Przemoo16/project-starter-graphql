from backend.libs.email.message import (
    EmailParticipants,
    HTMLMessage,
    build_html_message,
)


def test_build_html_message_builds_message() -> None:
    message = HTMLMessage(
        subject="Test subject",
        html_message="<html>HTML Message</html>",
        plain_message="Plain Message",
    )
    participants = EmailParticipants(
        sender="sender@email.com", receiver="receiver@email.com"
    )

    built_message = build_html_message(message, participants)

    assert "Content-Type: multipart/alternative" in built_message
    assert "Content-Type: text/html" in built_message
    assert "<html>HTML Message</html>" in built_message
    assert "Content-Type: text/plain" in built_message
    assert "Plain Message" in built_message
    assert "Subject: Test subject" in built_message
    assert "From: sender@email.com" in built_message
    assert "To: receiver@email.com" in built_message
