from pydantic import BaseModel, EmailStr

class LoginRegisterSchema(BaseModel):
    phone_or_email: str
    password: str


class RefreshSchema(BaseModel):
    refresh: str

