import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_pagination import Page, add_pagination
from sqlalchemy.orm import Session

from app import schemas, models
from app.accesses import payment_access, token_access
from app.database import get_db
from app.lib import get_remote_ip

router = APIRouter()
log = logging.getLogger(__name__)


# region Payment
@router.post("/add/")
def add_payment(request: Request, payment_method: str = Form(...), customer_id: UUID = Form(None),
                payment_amount: float = Form(...), payment_desc: str = Form(None), payment_date: datetime = Form(None),
                in_out: bool = Form(...), db: Session = Depends(get_db),
                current_user: schemas.Users = Depends(token_access.verify_admin_role),
                authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Payment added - %s", current_user.username, get_remote_ip(request))

    payment = payment_access.add_payment(db, payment_method=payment_method, customer_id=customer_id,
                                         payment_amount=payment_amount, payment_desc=payment_desc,
                                         payment_date=payment_date, in_out=in_out, create_user=current_user.username)

    if payment["status"] != 200:
        log.exception(payment["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=payment["status"], detail=payment["error_msg"])
    else:
        db.commit()
    return payment["result"]


@router.put("/edit-payment/")
def edit_payment(request: Request, id: UUID = Form(...), payment_method: str = Form(...),
                 customer_id: UUID = Form(None), payment_amount: float = Form(...), payment_desc: str = Form(None),
                 payment_date: datetime = Form(None), in_out: bool = Form(...), db: Session = Depends(get_db),
                 current_user: schemas.Users = Depends(token_access.verify_admin_role),
                 authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Payment edit - %s", current_user.username, get_remote_ip(request))

    payment = payment_access.edit_payment(db, id=id, payment_method=payment_method, customer_id=customer_id,
                                          payment_amount=payment_amount, payment_desc=payment_desc,
                                          payment_date=payment_date, in_out=in_out, create_user=current_user.username)

    if payment["status"] != 200:
        log.exception(payment["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=payment["status"], detail=payment["error_msg"])
    else:
        db.commit()
    return payment["result"]


@router.put("/edit-payment-amount/")
def edit_payment_amount(request: Request, id: UUID = Form(...), payment_amount: float = Form(...),
                        db: Session = Depends(get_db),
                        current_user: schemas.Users = Depends(token_access.verify_admin_role),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Payment edit amount - %s", current_user.username, get_remote_ip(request))

    payment = payment_access.edit_payment_amount(db, id=id, payment_amount=payment_amount,
                                                 create_user=current_user.username)

    if payment["status"] != 200:
        log.exception(payment["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=payment["status"], detail=payment["error_msg"])
    else:
        db.commit()
    return payment["result"]


@router.put("/change-state/{state}/")
def change_payment_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                         db: Session = Depends(get_db),
                         current_user: schemas.Users = Depends(token_access.verify_admin_role),
                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Payment payment state changed - %s", current_user.username, get_remote_ip(request))

    payment = payment_access.change_payment_state(db, id=id, state=state, create_user=current_user.username)

    if payment["status"] != 200:
        log.exception(payment["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=payment["status"], detail=payment["error_msg"])
    else:
        db.commit()
    return payment["result"]


@router.get("/detail/{id}/", response_model=schemas.PaymentView)
def get_payment_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                      current_user: schemas.Users = Depends(token_access.verify_admin_role),
                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Payment detail get by id - %s", current_user.username, get_remote_ip(request))

    payment = payment_access.get_payment_by_id(db, id=id)

    if payment["status"] != 200:
        log.exception(payment["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=payment["status"], detail=payment["error_msg"])
    return payment["result"]


@router.post("/search-active-by-info/", response_model=Page[schemas.PaymentView])
def search_active_by_info(request: Request, payment_method: str = Form(None), in_out: bool = Form(None),
                          start_date: str = Form(None), end_date: str = Form(None),
                          search_text: str = Form(None), db: Session = Depends(get_db),
                          current_user: schemas.Users = Depends(token_access.get_current_active_user),
                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Payment searched active by info - %s", current_user.username, get_remote_ip(request))

    payment_list_view = payment_access.search_active_by_info(db, payment_method=payment_method,
                                                             in_out=in_out, start_date=start_date,
                                                             end_date=end_date, search_text=search_text)

    if payment_list_view["status"] != 200:
        log.exception(payment_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=payment_list_view["status"], detail=payment_list_view["error_msg"])
    return payment_list_view["result"]


@router.post("/search-active-by-customer/", response_model=Page[schemas.PaymentView])
def search_active_by_customer(request: Request, customer_id: UUID = Form(...),
                              payment_method: str = Form(None), in_out: bool = Form(None),
                              start_date: str = Form(None), end_date: str = Form(None),
                              search_text: str = Form(None), db: Session = Depends(get_db),
                              current_user: schemas.Users = Depends(token_access.get_current_active_user),
                              authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Payment searched active by customer - %s", current_user.username, get_remote_ip(request))

    payment_list_view = payment_access.search_active_by_customer(db, customer_id=customer_id,
                                                                 payment_method=payment_method, in_out=in_out,
                                                                 start_date=start_date, end_date=end_date,
                                                                 search_text=search_text)

    if payment_list_view["status"] != 200:
        log.exception(payment_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=payment_list_view["status"], detail=payment_list_view["error_msg"])
    return payment_list_view["result"]


# endregion


add_pagination(router)
