from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    username: str
    email: EmailStr
    role: str

