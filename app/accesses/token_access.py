import datetime
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app import config, schemas
from app.accesses import user_access
from app.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token/")
list_admin = ["admin", "manager"]


# region Access
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = user_access.get_user(db, username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def authenticate_user_with_refresh_token(db: Session, username: str):
    user = user_access.get_user(db, username=username)
    if not user:
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=409,
        detail="validate_credentials_failed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = user_access.get_user(username=token_data.username, db=db)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: schemas.Users = Depends(get_current_user)):
    if not current_user.state.enabled:
        raise HTTPException(status_code=400, detail="user_inactive")
    return current_user


def verify_admin_role(current_user: schemas.Users = Depends(get_current_active_user)):
    if current_user.role.name not in list_admin:
        raise HTTPException(status_code=403, detail="not_permitted_operation")
    return current_user

# endregion
