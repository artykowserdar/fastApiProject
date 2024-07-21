import logging
from typing import List
from uuid import UUID

from fastapi import (APIRouter, Depends, File, Form, HTTPException, Request,
                     UploadFile)
from fastapi_jwt_auth import AuthJWT
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.orm import Session

from app import models, schemas
from app.accesses import token_access, user_access
from app.database import get_db
from app.lib import get_remote_ip

router = APIRouter()
log = logging.getLogger(__name__)


# region Users
@router.post("/add/{role}/")
def add_user(request: Request, role: str, username: str = Form(...), password: str = Form(...),
             customer_id: UUID = Form(None), image: UploadFile = File(None), db: Session = Depends(get_db),
             current_user: schemas.Users = Depends(token_access.verify_admin_role), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - User added - %s", current_user.username, get_remote_ip(request))

    user = user_access.add_user(db, username=username, password=password, role=role, image=image,
                                customer_id=customer_id, action_user=current_user.username)

    if user["status"] != 200:
        log.exception(user["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user["status"], detail=user["error_msg"])
    else:
        db.commit()
    return user["result"]


@router.post("/add-client/")
async def add_user(request: Request, phone: str = Form(...), lang: str = Form(...), phone_code: str = Form(None),
                   db: Session = Depends(get_db)):
    log.debug("Client added - %s", get_remote_ip(request))

    user = await user_access.add_client(db, phone=phone, lang=lang, phone_code=phone_code)

    if user["status"] != 200:
        log.exception(user["error_msg"] + ' - %s', get_remote_ip(request))
        raise HTTPException(status_code=user["status"], detail=user["error_msg"])
    else:
        db.commit()
    return user["result"]


@router.put("/edit/{role}/")
def edit(request: Request, role: str, username: str = Form(...), customer_id: UUID = Form(None),
         image: UploadFile = File(None), db: Session = Depends(get_db),
         current_user: schemas.Users = Depends(token_access.verify_admin_role), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - User edited - %s", current_user.username, get_remote_ip(request))

    user = user_access.edit_user(db, username=username, role=role, customer_id=customer_id, image=image,
                                 action_user=current_user.username)

    if user["status"] != 200:
        log.exception(user["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user["status"], detail=user["error_msg"])
    else:
        db.commit()
    return user["result"]


@router.put("/change-password/")
def change_user_password(request: Request, username: str = Form(...), password: str = Form(...),
                         db: Session = Depends(get_db),
                         current_user: schemas.Users = Depends(token_access.verify_admin_role),
                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - User password changed - %s", current_user.username, get_remote_ip(request))

    user = user_access.change_user_password(db, username=username, password=password,
                                            action_user=current_user.username)

    if user["status"] != 200:
        log.exception(user["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user["status"], detail=user["error_msg"])
    else:
        db.commit()
    return user["result"]


@router.put("/change-role/{role}/")
def change_user_role(role: models.UserRole, request: Request, username: str = Form(...), db: Session = Depends(get_db),
                     current_user: schemas.Users = Depends(token_access.verify_admin_role),
                     authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - User role changed - %s", current_user.username, get_remote_ip(request))

    user = user_access.change_user_role(db, username=username, role=role, action_user=current_user.username)

    if user["status"] != 200:
        log.exception(user["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user["status"], detail=user["error_msg"])
    else:
        db.commit()
    return user["result"]


@router.put("/change-state/{state}/")
def change_user_state(state: models.UserState, request: Request, username: str = Form(...),
                      db: Session = Depends(get_db),
                      current_user: schemas.Users = Depends(token_access.verify_admin_role),
                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - User state changed - %s", current_user.username, get_remote_ip(request))

    user = user_access.change_user_state(db, username=username, state=state, action_user=current_user.username)

    if user["status"] != 200:
        log.exception(user["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user["status"], detail=user["error_msg"])
    else:
        db.commit()
    return user["result"]


@router.get("/detail/{username}/", response_model=schemas.UserListView)
def get_user_by_username(username: str, request: Request, db: Session = Depends(get_db),
                         current_user: schemas.Users = Depends(token_access.verify_admin_role),
                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - User detail get by username - %s", current_user.username, get_remote_ip(request))

    user = user_access.get_user_by_username(db, username=username)

    if user["status"] != 200:
        log.exception(user["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user["status"], detail=user["error_msg"])
    return user["result"]


@router.get("/list/", response_model=List[schemas.Users])
def get_user_list(request: Request, db: Session = Depends(get_db),
                  current_user: schemas.Users = Depends(token_access.verify_admin_role),
                  authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Users listed - %s", current_user.username, get_remote_ip(request))

    user_list = user_access.get_user_list(db)

    if user_list["status"] != 200:
        log.exception(user_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user_list["status"], detail=user_list["error_msg"])
    return user_list["result"]


@router.get("/list-active/", response_model=List[schemas.Users])
def get_active_user_list(request: Request, db: Session = Depends(get_db),
                         current_user: schemas.Users = Depends(token_access.verify_admin_role),
                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Users listed active - %s", current_user.username, get_remote_ip(request))

    user_list = user_access.get_user_active_list(db)

    if user_list["status"] != 200:
        log.exception(user_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user_list["status"], detail=user_list["error_msg"])
    return user_list["result"]


@router.post("/search/", response_model=Page[schemas.Users])
def search(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
           current_user: schemas.Users = Depends(token_access.get_current_active_user), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Users searched - %s", current_user.username, get_remote_ip(request))

    user_list = user_access.search(db, search_text=search_text)

    if user_list["status"] != 200:
        log.exception(user_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user_list["status"], detail=user_list["error_msg"])
    return paginate(user_list["result"])


@router.post("/search-active/", response_model=Page[schemas.UserListView])
def search_active(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
                  current_user: schemas.Users = Depends(token_access.get_current_active_user),
                  authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Users searched active - %s", current_user.username, get_remote_ip(request))

    user_list = user_access.search_active(db, search_text=search_text)

    if user_list["status"] != 200:
        log.exception(user_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user_list["status"], detail=user_list["error_msg"])
    return paginate(user_list["result"])


@router.post("/search-active-type/", response_model=Page[schemas.UserCustomer])
def search_active_type(request: Request, search_text: str = Form(None), customer_type: str = Form(None),
                       db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.get_current_active_user),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Users searched active - %s", current_user.username, get_remote_ip(request))

    user_list = user_access.search_active_type(db, search_text=search_text, customer_type=customer_type)

    if user_list["status"] == 418:
        log.exception(user_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user_list["status"], detail=user_list["error_msg"])
    return paginate(user_list["result"])


@router.get("/list-user-action-log-by-user/{username}/", response_model=Page[schemas.UserActionLog])
def get_user_action_log_list_by_username(request: Request, username: str, db: Session = Depends(get_db),
                                         current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - User Action Log listed - %s", current_user.username, get_remote_ip(request))

    user_list = user_access.get_user_action_log_list_by_username(db, username=username)

    if user_list["status"] != 200:
        log.exception(user_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user_list["status"], detail=user_list["error_msg"])
    return user_list["result"]


@router.post("/logout/")
def log_out(request: Request, db: Session = Depends(get_db),
            current_user: schemas.Users = Depends(token_access.get_current_active_user),
            authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - User logged out - %s", current_user.username, get_remote_ip(request))

    user_list = user_access.log_out(db, username=current_user.username)

    if user_list["status"] != 200:
        log.exception(user_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=user_list["status"], detail=user_list["error_msg"])
    return user_list["result"]


# endregion


# region Logs
@router.get("/list-user-log-by-username/{username}/", response_model=List[schemas.Logs])
def get_user_log_list_username(request: Request, username: UUID, db: Session = Depends(get_db),
                               current_user: schemas.Users = Depends(token_access.verify_admin_role),
                               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - User Log - %s", current_user.username, get_remote_ip(request))

    db_log = user_access.get_user_log_list_username(db, username=username)

    if db_log["status"] != 200:
        raise HTTPException(status_code=db_log["status"], detail=db_log["error_msg"])
    return db_log["result"]


@router.get("/list-user-action-log-by-username/{username}/", response_model=List[schemas.Logs])
def get_user_action_log_list_username(request: Request, username: UUID, db: Session = Depends(get_db),
                                      current_user: schemas.Users = Depends(token_access.verify_admin_role),
                                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - User Action Log - %s", current_user.username, get_remote_ip(request))

    db_log = user_access.get_user_action_log_list_username(db, username=username)

    if db_log["status"] != 200:
        raise HTTPException(status_code=db_log["status"], detail=db_log["error_msg"])
    return db_log["result"]


# endregion


add_pagination(router)
