from pydantic import BaseModel, EmailStr, SecretStr


class EmailSettings(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_user: SecretStr
    smtp_password: SecretStr
    sender: EmailStr
