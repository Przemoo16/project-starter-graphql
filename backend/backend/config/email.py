from pydantic import BaseModel, EmailStr


class EmailSettings(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    sender: EmailStr
