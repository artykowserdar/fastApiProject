import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app import config, models
from app.accesses import token_access
from app.cruds import customer_crud, user_crud
from app.database import get_db
from app.lib import get_remote_ip

router = APIRouter()
log = logging.getLogger(__name__)


@router.post("/token/")
async def login_for_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    user = token_access.authenticate_user(db, form_data.username, form_data.password)
    log.debug('%s: token request: %s', form_data.username, get_remote_ip(request))
    try:
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Неверное имя пользователя или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        customer_id = None
        initials = None
        employee_type = None
        customer_type = None
        balance = 0
        phone = None
        rating = 0
        if user.username == 'admin':
            initials = {'en': 'Admin',
                        'ru': 'Админ',
                        'tm': 'Admin'}
            employee_type = 'Админ'
        else:
            db_customer = customer_crud.get_customer_by_username(db, user.username)
            if db_customer:
                if db_customer.employee_type == models.EmployeeType.driver and db_customer.current_balance <= 10:
                    raise HTTPException(
                        status_code=401,
                        detail="Пользователь достиг минимального баланса",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                customer_id = db_customer.id
                initials = db_customer.initials
                employee_type = db_customer.employee_type
                customer_type = db_customer.customer_type
                balance = db_customer.current_balance
                phone = db_customer.phone
                rating = db_customer.rating
        access_token = authorize.create_access_token(subject=user.username, expires_time=access_token_expires)
        refresh_token = authorize.create_refresh_token(subject=user.username)
        user_crud.add_user_action_log(db, user.username, models.UserAction.UserLogIn, None, None, None, None, None)
        avatar_full_path = config.IMAGE_IP_URL + '/avatars/1.jpg'
        avatar_full_temp_path = config.IMAGE_IP_URL + '/avatars/1.jpg'
        avatar_temp_path = config.IMAGE_URL + '/avatars/1.jpg'
        if user.avatar_name and user.avatar_name != 'no-image':
            avatar_full_path = config.IMAGE_IP_URL + '/avatars/' + user.avatar_name
            avatar_full_temp_path = config.IMAGE_IP_URL + '/avatars/tmb/' + user.avatar_name
            avatar_temp_path = config.IMAGE_URL + '/avatars/tmb/' + user.avatar_name
    except Exception:
        log.exception("%s - Error token request - %s", form_data.username, get_remote_ip(request))
        raise HTTPException(status_code=404, detail="ERROR")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "role": user.role,
            "username": user.username, "initials": initials, "avatar_name": user.avatar_name,
            "avatar_path": user.avatar_path, "avatar_full_path": avatar_full_path,
            "avatar_full_temp_path": avatar_full_temp_path, "avatar_temp_path": avatar_temp_path,
            "employee_type": employee_type, "customer_type": customer_type, "customer_id": customer_id,
            "balance": balance, "phone": phone, "rating": rating}


@router.post("/refresh/")
async def refresh_token(request: Request, authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    authorize.jwt_refresh_token_required()
    current_user = authorize.get_jwt_subject()
    user = token_access.authenticate_user_with_refresh_token(db, current_user)
    try:
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        customer_id = None
        initials = None
        employee_type = None
        customer_type = None
        balance = 0
        phone = None
        rating = 0
        if user.username == 'admin':
            initials = {'en': 'Admin',
                        'ru': 'Админ',
                        'tm': 'Admin'}
            employee_type = 'Админ'
        else:
            db_customer = customer_crud.get_customer_by_username(db, user.username)
            if db_customer:
                if db_customer.employee_type == models.EmployeeType.driver and db_customer.current_balance <= 10:
                    raise HTTPException(
                        status_code=401,
                        detail="Пользователь достиг минимального баланса",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                customer_id = db_customer.id
                initials = db_customer.initials
                employee_type = db_customer.employee_type
                customer_type = db_customer.customer_type
                balance = db_customer.current_balance
                phone = db_customer.phone
                rating = db_customer.rating
        new_access_token = authorize.create_access_token(subject=user.username, expires_time=access_token_expires)
        refresh_token = authorize.create_refresh_token(subject=user.username)
        avatar_full_path = config.IMAGE_IP_URL + '/avatars/1.jpg'
        avatar_full_temp_path = config.IMAGE_IP_URL + '/avatars/1.jpg'
        avatar_temp_path = config.IMAGE_URL + '/avatars/1.jpg'
        if user.avatar_name and user.avatar_name != 'no-image':
            avatar_full_path = config.IMAGE_IP_URL + '/avatars/' + user.avatar_name
            avatar_full_temp_path = config.IMAGE_IP_URL + '/avatars/tmb/' + user.avatar_name
            avatar_temp_path = config.IMAGE_URL + '/avatars/tmb/' + user.avatar_name
    except Exception:
        log.exception("%s - Error token request - %s", current_user, get_remote_ip(request))
        raise HTTPException(status_code=404, detail="ERROR")
    return {"access_token": new_access_token, "refresh_token": refresh_token, "token_type": "bearer",
            "role": user.role, "username": user.username, "initials": initials, "avatar_name": user.avatar_name,
            "avatar_path": user.avatar_path, "avatar_full_path": avatar_full_path,
            "avatar_full_temp_path": avatar_full_temp_path, "avatar_temp_path": avatar_temp_path,
            "employee_type": employee_type, "customer_type": customer_type, "customer_id": customer_id,
            "balance": balance, "phone": phone, "rating": rating}


@router.get('/protected')
def protected(authorize: AuthJWT = Depends()):
    authorize.jwt_required()

    current_user = authorize.get_jwt_subject()
    return {"user": current_user}
