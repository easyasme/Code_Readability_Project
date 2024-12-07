from datetime import datetime, timedelta, UTC

import jwt
from pydantic import ValidationError

from src.models.jwt import JWTMeta, JWTUser
from src.models.users import User

JWT_SUBJECT = "access"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
ACCESS_TOKEN_EXPIRE_TIMEDELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


def create_jwt_token(content: dict[str, str], secret_key: str, expires_delta: timedelta) -> str:
    to_encode = content.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update(JWTMeta(exp=expire, sub=JWT_SUBJECT).model_dump())
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)


def create_access_token_for_user(user: User, secret_key: str) -> str:
    return create_jwt_token(
        JWTUser(username=user.username).model_dump(), secret_key, ACCESS_TOKEN_EXPIRE_TIMEDELTA
    )


def get_username_from_token(token: str, secret_key: str) -> str:
    try:
        return JWTUser(**jwt.decode(token, secret_key, algorithms=[ALGORITHM])).username
    except jwt.PyJWTError as decode_error:
        raise ValueError("Unable to decode JWT token") from decode_error
    except ValidationError as validation_error:
        raise ValueError("Malformed payload in token") from validation_error
