import logging
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_pagination import Page, add_pagination
from sqlalchemy.orm import Session

from app import schemas
from app.accesses import order_access, token_access
from app.database import get_db
from app.lib import get_remote_ip

router = APIRouter()
log = logging.getLogger(__name__)


# region Order
@router.post("/add/")
async def add_order(request: Request, vehicle_id: UUID = Form(None), client_id: UUID = Form(None),
                    service_id: UUID = Form(...), rate_id: UUID = Form(...), shift_id: UUID = Form(...),
                    district_id_from: UUID = Form(None), district_id_to: UUID = Form(None),
                    address_from: str = Form(...), address_to: str = Form(None), coordinates_from: str = Form(None),
                    coordinates_to: str = Form(None), order_desc: str = Form(None), order_date: datetime = Form(None),
                    pay_discount_prc: float = Form(None), phone: str = Form(None), fullname: str = Form(None),
                    lang: str = Form(None), db: Session = Depends(get_db),
                    current_user: schemas.Users = Depends(token_access.get_current_active_user),
                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order added - %s", current_user.username, get_remote_ip(request))

    order = await order_access.add_order(db, vehicle_id=vehicle_id, client_id=client_id, service_id=service_id,
                                         rate_id=rate_id, shift_id=shift_id, district_id_from=district_id_from,
                                         district_id_to=district_id_to, address_from=address_from,
                                         address_to=address_to, coordinates_from=coordinates_from,
                                         coordinates_to=coordinates_to, order_desc=order_desc, order_date=order_date,
                                         pay_discount_prc=pay_discount_prc, phone=phone, fullname=fullname,
                                         lang=lang, create_user=current_user.username)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    else:
        db.commit()
    return order["result"]


@router.put("/add-order-driver/")
async def add_order_driver(request: Request, id: UUID = Form(...), vehicle_id: UUID = Form(None),
                           lang: str = Form(None), db: Session = Depends(get_db),
                           current_user: schemas.Users = Depends(token_access.get_current_active_user),
                           authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order driver addd - %s", current_user.username, get_remote_ip(request))

    order = await order_access.add_order_driver(db, id=id, vehicle_id=vehicle_id, lang=lang,
                                                create_user=current_user.username)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    else:
        db.commit()
    return order["result"]


@router.put("/remove-order-driver/")
async def remove_order_driver(request: Request, id: UUID = Form(...), lang: str = Form(None),
                              db: Session = Depends(get_db),
                              current_user: schemas.Users = Depends(token_access.get_current_active_user),
                              authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order driver removed - %s", current_user.username, get_remote_ip(request))

    order = await order_access.remove_order_driver(db, id=id, lang=lang, create_user=current_user.username)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    else:
        db.commit()
    return order["result"]


@router.put("/change-order-state/{order_state}/")
def change_order_state(request: Request, order_state: str, id: UUID = Form(...), db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.get_current_active_user),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order order state changed - %s", current_user.username, get_remote_ip(request))

    order = order_access.change_order_state(db, id=id, order_state=order_state, create_user=current_user.username)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    else:
        db.commit()
    return order["result"]


@router.put("/accept-order/")
async def accept_order(request: Request, id: UUID = Form(...), lang: str = Form(None), db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.get_current_active_user),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order accept state - %s", current_user.username, get_remote_ip(request))

    order = await order_access.accept_order(db, id=id, create_user=current_user.username, lang=lang)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    else:
        db.commit()
    return order["result"]


@router.put("/take-postponed-order/")
async def take_postponed_order(request: Request, id: UUID = Form(...), driver_id: UUID = Form(...),
                               vehicle_id: UUID = Form(...), lang: str = Form(None), db: Session = Depends(get_db),
                               current_user: schemas.Users = Depends(token_access.get_current_active_user),
                               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order postponed take state - %s", current_user.username, get_remote_ip(request))

    order = await order_access.take_postponed_order(db, id=id, driver_id=driver_id, vehicle_id=vehicle_id,
                                                    create_user=current_user.username, lang=lang)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    else:
        db.commit()
    return order["result"]


@router.put("/accept-postponed-order/")
async def accept_postponed_order(request: Request, id: UUID = Form(...), lang: str = Form(None),
                                 db: Session = Depends(get_db),
                                 current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                 authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order postponed accept state - %s", current_user.username, get_remote_ip(request))

    order = await order_access.accept_postponed_order(db, id=id, create_user=current_user.username, lang=lang)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    else:
        db.commit()
    return order["result"]


@router.put("/start-order/")
async def start_order(request: Request, id: UUID = Form(...), lang: str = Form(None), db: Session = Depends(get_db),
                      current_user: schemas.Users = Depends(token_access.get_current_active_user),
                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order start state - %s", current_user.username, get_remote_ip(request))

    order = await order_access.start_order(db, id=id, create_user=current_user.username, lang=lang)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    else:
        db.commit()
    return order["result"]


@router.put("/finish-order/")
async def finish_order(request: Request, id: UUID = Form(...), pay_total: float = Form(...),
                       order_distance: float = Form(...), order_time: float = Form(...),
                       order_wait_time: float = Form(...), lang: str = Form(None), db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.get_current_active_user),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order finish state - %s", current_user.username, get_remote_ip(request))

    order = await order_access.finish_order(db, id=id, pay_total=pay_total, order_distance=order_distance,
                                            order_time=order_time, order_wait_time=order_wait_time,
                                            create_user=current_user.username, lang=lang)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    else:
        db.commit()
    return order["result"]


@router.put("/cancel-order/")
async def cancel_order(request: Request, id: UUID = Form(...), lang: str = Form(None), db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.get_current_active_user),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order cancel state - %s", current_user.username, get_remote_ip(request))

    order = await order_access.cancel_order(db, id=id, create_user=current_user.username, lang=lang)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    else:
        db.commit()
    return order["result"]


@router.put("/reject-order/")
async def reject_order(request: Request, id: UUID = Form(...), district_id: UUID = Form(None),
                       db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.get_current_active_user),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order reject state - %s", current_user.username, get_remote_ip(request))

    order = await order_access.reject_order(db, id=id, district_id=district_id, create_user=current_user.username)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    else:
        db.commit()
    return order["result"]


@router.get("/detail/{id}/", response_model=schemas.OrderView)
def get_order_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                    current_user: schemas.Users = Depends(token_access.get_current_active_user),
                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order detail get by id - %s", current_user.username, get_remote_ip(request))

    order = order_access.get_order_by_id(db, id=id)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    return order["result"]


@router.get("/list-active-post-by-service/{driver_id}/{vehicle_id}/", response_model=List[schemas.OrderView])
def get_order_post_list_by_service(request: Request, driver_id: UUID, vehicle_id: UUID, db: Session = Depends(get_db),
                                   current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                   authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order postponed listed active by service - %s", current_user.username,
              get_remote_ip(request))

    order_list_view = order_access.get_order_post_list_by_service(db, driver_id=driver_id, vehicle_id=vehicle_id)

    if order_list_view["status"] != 200:
        log.exception(order_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order_list_view["status"], detail=order_list_view["error_msg"])
    return order_list_view["result"]


@router.get("/list-active-post-by-info-service/{driver_id}/{vehicle_id}/", response_model=List[schemas.OrderView])
def get_order_post_list_by_info_service(request: Request, driver_id: UUID, vehicle_id: UUID,
                                        db: Session = Depends(get_db),
                                        current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order postponed listed active by info service - %s", current_user.username,
              get_remote_ip(request))

    order_list_view = order_access.get_order_post_list_by_info_service(db, driver_id=driver_id, vehicle_id=vehicle_id)

    if order_list_view["status"] != 200:
        log.exception(order_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order_list_view["status"], detail=order_list_view["error_msg"])
    return order_list_view["result"]


@router.post("/search-active-by-info/", response_model=Page[schemas.OrderView])
def search_active_by_info(request: Request, order_type: str = Form(None), order_state: str = Form(None),
                          service_id: str = Form(None), start_date: str = Form(None), end_date: str = Form(None),
                          search_text: str = Form(None), db: Session = Depends(get_db),
                          current_user: schemas.Users = Depends(token_access.get_current_active_user),
                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order searched active by info - %s", current_user.username, get_remote_ip(request))

    order_list_view = order_access.search_active_by_info(db, order_type=order_type, order_state=order_state,
                                                         service_id=service_id, start_date=start_date,
                                                         end_date=end_date, search_text=search_text)

    if order_list_view["status"] != 200:
        log.exception(order_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order_list_view["status"], detail=order_list_view["error_msg"])
    return order_list_view["result"]


@router.post("/search-active-by-driver/", response_model=Page[schemas.OrderView])
def search_active_by_driver(request: Request, driver_id: UUID = Form(...), order_type: str = Form(None),
                            order_state: str = Form(None), service_id: str = Form(None),
                            start_date: str = Form(None), end_date: str = Form(None),
                            search_text: str = Form(None), db: Session = Depends(get_db),
                            current_user: schemas.Users = Depends(token_access.get_current_active_user),
                            authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order searched active by driver - %s", current_user.username, get_remote_ip(request))

    order_list_view = order_access.search_active_by_driver(db, driver_id=driver_id, order_type=order_type,
                                                           order_state=order_state, service_id=service_id,
                                                           start_date=start_date, end_date=end_date,
                                                           search_text=search_text)

    if order_list_view["status"] != 200:
        log.exception(order_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order_list_view["status"], detail=order_list_view["error_msg"])
    return order_list_view["result"]


@router.post("/search-active-by-client/", response_model=Page[schemas.OrderView])
def search_active_by_client(request: Request, client_id: UUID = Form(...), order_type: str = Form(None),
                            order_state: str = Form(None), service_id: str = Form(None),
                            start_date: str = Form(None), end_date: str = Form(None),
                            search_text: str = Form(None), db: Session = Depends(get_db),
                            current_user: schemas.Users = Depends(token_access.get_current_active_user),
                            authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order searched active by client - %s", current_user.username, get_remote_ip(request))

    order_list_view = order_access.search_active_by_client(db, client_id=client_id, order_type=order_type,
                                                           order_state=order_state, service_id=service_id,
                                                           start_date=start_date, end_date=end_date,
                                                           search_text=search_text)

    if order_list_view["status"] != 200:
        log.exception(order_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order_list_view["status"], detail=order_list_view["error_msg"])
    return order_list_view["result"]


# endregion


# region Order History
@router.get("/history-list-by-order/{order_id}/", response_model=List[schemas.OrderHistoryView])
def get_order_history_list_by_order(request: Request, order_id: UUID, db: Session = Depends(get_db),
                                    current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Order history list get by order_id - %s", current_user.username, get_remote_ip(request))

    order = order_access.get_order_history_list_by_order(db, order_id=order_id)

    if order["status"] != 200:
        log.exception(order["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=order["status"], detail=order["error_msg"])
    return order["result"]


# endregion


add_pagination(router)
