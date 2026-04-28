from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False
    is_verified: bool = False


class UserCreate(UserBase):
    password: str
    accepted_terms: bool = Field(..., description='Пользователь должен принять Пользовательское соглашение')

    @field_validator('accepted_terms')
    @classmethod
    def validate_terms(cls, value):
        if not value:
            raise ValueError('Необходимо принять Пользовательское соглашение')
        return value


class UserOut(UserBase):
    id: int
    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordChangeRequest(BaseModel):
    old_password: str = Field(...)
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, value):
        if not any(char.isupper() for char in value):
            raise ValueError("New password must contain at least one uppercase letter.")
        if not any(char.islower() for char in value):
            raise ValueError("New password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in value):
            raise ValueError("New password must contain at least one digit.")
        return value


class PasswordResetEmailRequest(BaseModel):
    email: EmailStr


class PasswordResetRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, value):
        if not any(char.isupper() for char in value):
            raise ValueError("New password must contain at least one uppercase letter.")
        if not any(char.islower() for char in value):
            raise ValueError("New password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in value):
            raise ValueError("New password must contain at least one digit.")
        return value
