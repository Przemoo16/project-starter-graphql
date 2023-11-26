from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
from ssl import create_default_context

_ssl_context = create_default_context()


@dataclass
class HTMLMessage:
    subject: str
    html_message: str
    plain_message: str


@dataclass
class EmailParticipants:
    sender: str
    receiver: str


@dataclass
class SMTPServer:
    host: str
    port: int
    user: str
    password: str


def send_html_email(
    message: HTMLMessage, participants: EmailParticipants, smtp_server: SMTPServer
) -> None:
    built_message = build_html_message(message, participants)
    _send_email(built_message, participants, smtp_server)


def build_html_message(message: HTMLMessage, participants: EmailParticipants) -> str:
    built_message = MIMEMultipart("alternative")
    built_message["Subject"] = message.subject
    built_message["From"] = participants.sender
    built_message["To"] = participants.receiver
    built_message.attach(MIMEText(message.plain_message, "plain"))
    built_message.attach(MIMEText(message.html_message, "html"))
    return built_message.as_string()


def _send_email(
    message: str, participants: EmailParticipants, smtp_server: SMTPServer
) -> None:
    with SMTP(smtp_server.host, smtp_server.port) as server:
        server.ehlo()
        server.starttls(context=_ssl_context)
        server.ehlo()
        server.login(smtp_server.user, smtp_server.password)
        server.sendmail(participants.sender, participants.receiver, message)
