"""
Auth API — JWT 认证 + 角色权限
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from datetime import datetime, timedelta
import jwt
import os

router = APIRouter(
    prefix="/auth", tags=["auth"]
)

SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "change_this_secret"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 临时用户（可换 DB）
USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
    },
    "user": {
        "password": "user123",
        "role": "viewer",
    },
}

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token"
)


def create_access_token(
    data: dict,
    expires_delta: timedelta = None,
):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        or timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, SECRET_KEY, algorithm=ALGORITHM
    )


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token expired",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    return verify_token(token)


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = USERS.get(form_data.username)
    if (
        not user
        or user["password"] != form_data.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect credentials",
        )
    token = create_access_token(
        {
            "sub": form_data.username,
            "role": user["role"],
        }
    )
    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/me")
async def get_me(
    current_user=Depends(get_current_user),
):
    return current_user
