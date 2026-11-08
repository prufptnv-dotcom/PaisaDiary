from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)) -> User:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key,
                             algorithms=[settings.jwt_algorithm])
        if payload.get("type") != "access":
            raise ValueError("Wrong token type")
        user_id = UUID(payload["sub"])
        token_version = payload.get("ver")
        if not isinstance(token_version, int) or token_version < 0:
            raise ValueError("Missing or invalid token version")
    except (jwt.PyJWTError, ValueError, KeyError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired access token",
                            headers={"WWW-Authenticate": "Bearer"})

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User no longer exists",
                            headers={"WWW-Authenticate": "Bearer"})
    if token_version != user.token_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Access token has been revoked",
                            headers={"WWW-Authenticate": "Bearer"})
    return user
