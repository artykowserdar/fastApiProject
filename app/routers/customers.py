import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile, File
from fastapi_jwt_auth import AuthJWT
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.orm import Session

from app import models, schemas
from app.accesses import customer_access, token_access
from app.database import get_db
from app.lib import get_remote_ip

router = APIRouter()
log = logging.getLogger(__name__)


# region Customer
@router.post("/add/{customer_type}/")
def add_customer(request: Request, customer_type: models.CustomerType, fullname: str = Form(...),
                 initials: str = Form(None), address: str = Form(None), birth_date: str = Form(None),
                 birth_place: str = Form(None), gender: str = Form(...), username: str = Form(None),
                 employee_type: str = Form(None), discount_percent: float = Form(None),
                 discount_limit: float = Form(None), card_no: str = Form(None), phone: str = Form(None),
                 image: UploadFile = File(None), db: Session = Depends(get_db),
                 current_user: schemas.Users = Depends(token_access.verify_admin_role), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer added - %s", current_user.username, get_remote_ip(request))

    customer = customer_access.add_customer(db, username=username, fullname=fullname, initials=initials,
                                            address=address, birth_date=birth_date, birth_place=birth_place,
                                            gender=gender, customer_type=customer_type, employee_type=employee_type,
                                            discount_percent=discount_percent, discount_limit=discount_limit,
                                            card_no=card_no, phone=phone, image=image,
                                            action_user=current_user.username)

    if customer["status"] != 200:
        log.exception(customer["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer["status"], detail=customer["error_msg"])
    else:
        db.commit()
    return customer["result"]


@router.put("/edit/{customer_type}/")
def edit_customer(request: Request, customer_type: models.CustomerType, id: UUID = Form(...), fullname: str = Form(...),
                  initials: str = Form(None), address: str = Form(None), birth_date: str = Form(None),
                  birth_place: str = Form(None), gender: str = Form(...), employee_type: str = Form(None),
                  discount_percent: float = Form(None), discount_limit: float = Form(None), card_no: str = Form(None),
                  phone: str = Form(None), image: UploadFile = File(None), db: Session = Depends(get_db),
                  current_user: schemas.Users = Depends(token_access.verify_admin_role),
                  authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer edited - %s", current_user.username, get_remote_ip(request))

    customer = customer_access.edit_customer(db, id=id, fullname=fullname, initials=initials,
                                             customer_type=customer_type, address=address, birth_date=birth_date,
                                             birth_place=birth_place, gender=gender, employee_type=employee_type,
                                             discount_percent=discount_percent, discount_limit=discount_limit,
                                             card_no=card_no, phone=phone, image=image,
                                             action_user=current_user.username)

    if customer["status"] != 200:
        log.exception(customer["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer["status"], detail=customer["error_msg"])
    else:
        db.commit()
    return customer["result"]


@router.put("/add-blacklist/")
def add_customer_blacklist(request: Request, id: UUID = Form(...), blacklist: bool = Form(...),
                           db: Session = Depends(get_db),
                           current_user: schemas.Users = Depends(token_access.verify_admin_role),
                           authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer added blacklist - %s", current_user.username, get_remote_ip(request))

    customer = customer_access.add_customer_blacklist(db, id=id, blacklist=blacklist, action_user=current_user.username)

    if customer["status"] != 200:
        log.exception(customer["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer["status"], detail=customer["error_msg"])
    else:
        db.commit()
    return customer["result"]


@router.put("/change-state/{state}/")
def change_customer_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                          db: Session = Depends(get_db),
                          current_user: schemas.Users = Depends(token_access.verify_admin_role),
                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer state changed - %s", current_user.username, get_remote_ip(request))

    customer = customer_access.change_customer_state(db, id=id, state=state, action_user=current_user.username)

    if customer["status"] != 200:
        log.exception(customer["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer["status"], detail=customer["error_msg"])
    else:
        db.commit()
    return customer["result"]


@router.get("/detail/{id}/", response_model=schemas.CustomerView)
def get_customer_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.get_current_active_user),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer detail get by id - %s", current_user.username, get_remote_ip(request))

    customer = customer_access.get_customer_by_id(db, id=id)

    if customer["status"] != 200:
        log.exception(customer["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer["status"], detail=customer["error_msg"])
    return customer["result"]


@router.get("/detail-by-phone/{phone}/", response_model=schemas.Customers)
def get_customer_by_phone(request: Request, phone: str, db: Session = Depends(get_db),
                          current_user: schemas.Users = Depends(token_access.get_current_active_user),
                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer detail get by phone - %s", current_user.username, get_remote_ip(request))

    customer = customer_access.get_customer_by_phone(db, phone=phone)

    if customer["status"] != 200:
        log.exception(customer["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer["status"], detail=customer["error_msg"])
    return customer["result"]


@router.get("/detail-by-username/{username}/", response_model=schemas.Customers)
def get_customer_by_username(request: Request, username: str, db: Session = Depends(get_db),
                             current_user: schemas.Users = Depends(token_access.get_current_active_user),
                             authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer detail get by username - %s", current_user.username, get_remote_ip(request))

    customer = customer_access.get_customer_by_username(db, username=username)

    if customer["status"] != 200:
        log.exception(customer["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer["status"], detail=customer["error_msg"])
    return customer["result"]


@router.get("/list-active/", response_model=List[schemas.CustomerView])
def get_active_customer_list(request: Request, db: Session = Depends(get_db),
                             current_user: schemas.Users = Depends(token_access.get_current_active_user),
                             authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customers listed active - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.get_customer_active_list(db)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-by-type/{customer_type}/", response_model=List[schemas.CustomerView])
def get_customer_active_list_by_type(request: Request, customer_type: str, db: Session = Depends(get_db),
                                     current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                     authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customers listed active by customer_type - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.get_customer_active_list_by_type(db, customer_type=customer_type)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-employee/", response_model=List[schemas.Customers])
def get_customer_active_list_employee(request: Request, db: Session = Depends(get_db),
                                      current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customers listed active by customer_type - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.get_customer_active_list_employee(db)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-employee-driver/", response_model=List[schemas.Customers])
def get_customer_active_list_employee_driver(request: Request, db: Session = Depends(get_db),
                                             current_user: schemas.Users = Depends(
                                                 token_access.get_current_active_user),
                                             authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customers listed active by customer_type - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.get_customer_active_list_employee_driver(db)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-by-type-not-blacklist/{customer_type}/",
            response_model=List[schemas.CustomerView])
def get_customer_active_list_by_type_not_blacklist(request: Request, customer_type: models.CustomerType,
                                                   db: Session = Depends(get_db),
                                                   current_user: schemas.Users = Depends(
                                                       token_access.get_current_active_user),
                                                   authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customers listed active by customer_type not in blacklist - %s", current_user.username,
              get_remote_ip(request))

    customer_list = customer_access.get_customer_active_list_by_type_not_blacklist(db, customer_type=customer_type)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-employee-not-assigned/", response_model=List[schemas.CustomerView])
def get_customer_active_list_not_assigned(request: Request, db: Session = Depends(get_db),
                                          current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customers listed active by customer_type not in blacklist - %s", current_user.username,
              get_remote_ip(request))

    customer_list = customer_access.get_customer_active_list_not_assigned(db)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-employee-not-assigned-user/{username}/", response_model=List[schemas.CustomerView])
def get_customer_active_list_not_assigned_user(request: Request, username: str, db: Session = Depends(get_db),
                                               current_user: schemas.Users = Depends(
                                                   token_access.get_current_active_user),
                                               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customers listed active by customer_type not in blacklist - %s", current_user.username,
              get_remote_ip(request))

    customer_list = customer_access.get_customer_active_list_not_assigned_user(db, username=username)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-by-employee-type/{employee_type}/", response_model=List[schemas.CustomerView])
def get_customer_active_list_by_employee_type(request: Request, employee_type: models.EmployeeType,
                                              db: Session = Depends(get_db),
                                              current_user: schemas.Users = Depends(
                                                  token_access.get_current_active_user),
                                              authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customers listed active by customer_type - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.get_customer_active_list_by_employee_type(db, employee_type=employee_type)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.post("/search/", response_model=Page[schemas.CustomerView])
def search_by_fullname(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.get_current_active_user),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customers searched - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.search(db, search_text=search_text)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return paginate(customer_list["result"])


@router.post("/search-active/", response_model=Page[schemas.CustomerView])
def search_by_fullname_active(request: Request, search_text: str = Form(None),
                              db: Session = Depends(get_db),
                              current_user: schemas.Users = Depends(token_access.get_current_active_user),
                              authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customers searched active - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.search_active(db, search_text=search_text)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return paginate(customer_list["result"])


@router.post("/search-active-by-type/", response_model=Page[schemas.CustomerView])
def search_by_fullname_active_by_type(request: Request, search_text: str = Form(None),
                                      customer_type: models.CustomerType = Form(...), db: Session = Depends(get_db),
                                      current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customers searched active by type - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.search_active_by_type(db, search_text=search_text, customer_type=customer_type)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return paginate(customer_list["result"])


@router.post("/search-active-by-employee-type/", response_model=Page[schemas.CustomerView])
def search_active_by_employee_type(request: Request, search_text: str = Form(None),
                                   employee_type: str = Form(None), db: Session = Depends(get_db),
                                   current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                   authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customers searched active by type - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.search_active_by_employee_type(db, search_text=search_text,
                                                                   employee_type=employee_type)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return paginate(customer_list["result"])


# endregion


# region Client Address History
@router.put("/change-address-history-state/{state}/")
def change_client_address_history_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                                        db: Session = Depends(get_db),
                                        current_user: schemas.Users = Depends(token_access.verify_admin_role),
                                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Client Address History state changed - %s", current_user.username, get_remote_ip(request))

    customer = customer_access.change_client_address_history_state(db, id=id, state=state,
                                                                   action_user=current_user.username)

    if customer["status"] != 200:
        log.exception(customer["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer["status"], detail=customer["error_msg"])
    else:
        db.commit()
    return customer["result"]


@router.get("/list-address-history/", response_model=List[schemas.ClientAddressHistory])
def get_client_address_history_list(request: Request, db: Session = Depends(get_db),
                                    current_user: schemas.Users = Depends(token_access.verify_admin_role),
                                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Client Address History listed - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.get_client_address_history_list(db)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-address-history/", response_model=List[schemas.ClientAddressHistory])
def get_client_address_history_active_list(request: Request, db: Session = Depends(get_db),
                                           current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                           authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Client Address History listed active - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.get_client_address_history_active_list(db)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-address-history-by-client/{client_id}/",
            response_model=List[schemas.ClientAddressHistory])
def get_client_address_history_active_list_by_client(request: Request, client_id: UUID, db: Session = Depends(get_db),
                                                     current_user: schemas.Users = Depends(
                                                         token_access.get_current_active_user),
                                                     authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Client Address History listed active by client_id - %s", current_user.username,
              get_remote_ip(request))

    customer_list = customer_access.get_client_address_history_active_list_by_client(db, client_id=client_id)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-address-history-by-type/{client_id}/{address_type}/",
            response_model=List[schemas.ClientAddressHistory])
def get_client_address_history_active_list_by_client_type(request: Request, client_id: UUID, address_type: str,
                                                          db: Session = Depends(get_db),
                                                          current_user: schemas.Users = Depends(
                                                              token_access.get_current_active_user),
                                                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Client Address History listed active by client_id and type - %s", current_user.username,
              get_remote_ip(request))

    customer_list = customer_access.get_client_address_history_active_list_by_client_type(db, client_id=client_id,
                                                                                          address_type=address_type)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-address-history-by-type-order/{client_id}/{address_type}/")
def get_client_address_history_active_list_by_type_order(request: Request, client_id: UUID, address_type: str,
                                                         db: Session = Depends(get_db),
                                                         current_user: schemas.Users = Depends(
                                                             token_access.get_current_active_user),
                                                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Client Address History listed active by client_id and type - %s", current_user.username,
              get_remote_ip(request))

    customer_list = customer_access.get_client_address_history_active_list_by_type_order(db, client_id=client_id,
                                                                                         address_type=address_type)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.post("/search-active-address-history-by-employee-type/", response_model=Page[schemas.ClientAddressHistory])
def search_active_client_address_history_by_client_type(request: Request, search_text: str = Form(None),
                                                        address_type: str = Form(None), client_id: str = Form(...),
                                                        db: Session = Depends(get_db),
                                                        current_user: schemas.Users = Depends(
                                                            token_access.get_current_active_user),
                                                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Client Address History searched active by type - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.search_active_client_address_history_by_client_type(db, search_text=search_text,
                                                                                        client_id=client_id,
                                                                                        address_type=address_type)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return paginate(customer_list["result"])


# endregion


# region Customer Ratings
@router.post("/add-customer-rating/")
def add_customer_rating(request: Request, set_customer_id: UUID = Form(...), get_customer_id: UUID = Form(...),
                        rating: int = Form(...), comment: str = Form(None), db: Session = Depends(get_db),
                        current_user: schemas.Users = Depends(token_access.verify_admin_role),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer Ratings added - %s", current_user.username, get_remote_ip(request))

    customer = customer_access.add_customer_rating(db, set_customer_id=set_customer_id, get_customer_id=get_customer_id,
                                                   rating=rating, comment=comment, action_user=current_user.username)

    if customer["status"] != 200:
        log.exception(customer["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer["status"], detail=customer["error_msg"])
    else:
        db.commit()
    return customer["result"]


@router.put("/edit-customer-rating/")
def edit_customer_rating(request: Request, id: UUID = Form(...), rating: int = Form(...),
                         comment: str = Form(None), db: Session = Depends(get_db),
                         current_user: schemas.Users = Depends(token_access.verify_admin_role),
                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer Ratings edited - %s", current_user.username, get_remote_ip(request))

    customer = customer_access.edit_customer_rating(db, id=id, rating=rating, comment=comment,
                                                    action_user=current_user.username)

    if customer["status"] != 200:
        log.exception(customer["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer["status"], detail=customer["error_msg"])
    else:
        db.commit()
    return customer["result"]


@router.put("/update-customer-rating/{state}/")
def update_customer_rating_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                                 rating: int = Form(...), comment: str = Form(None), db: Session = Depends(get_db),
                                 current_user: schemas.Users = Depends(token_access.verify_admin_role),
                                 authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer Ratings edited - %s", current_user.username, get_remote_ip(request))

    customer = customer_access.update_customer_rating_state(db, id=id, rating=rating, comment=comment, state=state,
                                                            action_user=current_user.username)

    if customer["status"] != 200:
        log.exception(customer["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer["status"], detail=customer["error_msg"])
    else:
        db.commit()
    return customer["result"]


@router.put("/change-customer-rating-state/{state}/")
def change_customer_rating_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                                 db: Session = Depends(get_db),
                                 current_user: schemas.Users = Depends(token_access.verify_admin_role),
                                 authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer Ratings state changed - %s", current_user.username, get_remote_ip(request))

    customer = customer_access.change_customer_rating_state(db, id=id, state=state,
                                                            action_user=current_user.username)

    if customer["status"] != 200:
        log.exception(customer["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer["status"], detail=customer["error_msg"])
    else:
        db.commit()
    return customer["result"]


@router.get("/customer-rating-detail/{id}/", response_model=List[schemas.CustomerRatings])
def get_customer_rating_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                              current_user: schemas.Users = Depends(token_access.verify_admin_role),
                              authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer Ratings detail by id - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.get_customer_rating_by_id(db, id=id)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-customer-rating/", response_model=List[schemas.CustomerRatings])
def get_customer_rating_active_list(request: Request, db: Session = Depends(get_db),
                                    current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer Ratings listed active - %s", current_user.username, get_remote_ip(request))

    customer_list = customer_access.get_customer_rating_active_list(db)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-customer-rating-by-set-customer/{set_customer_id}/",
            response_model=List[schemas.CustomerRatings])
def get_customer_rating_active_list_by_set_customer(request: Request, set_customer_id: UUID,
                                                    db: Session = Depends(get_db),
                                                    current_user: schemas.Users = Depends(
                                                        token_access.get_current_active_user),
                                                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer Ratings listed active by set_customer_id - %s", current_user.username,
              get_remote_ip(request))

    customer_list = customer_access.get_customer_rating_active_list_by_set_customer(db, set_customer_id=set_customer_id)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.get("/list-active-customer-rating-by-get-customer/{get_customer_id}/",
            response_model=List[schemas.CustomerRatings])
def get_customer_rating_active_list_by_get_customer(request: Request, get_customer_id: UUID,
                                                    db: Session = Depends(get_db),
                                                    current_user: schemas.Users = Depends(
                                                        token_access.get_current_active_user),
                                                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer Ratings listed active by get_customer_id - %s", current_user.username,
              get_remote_ip(request))

    customer_list = customer_access.get_customer_rating_active_list_by_get_customer(db, get_customer_id=get_customer_id)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return customer_list["result"]


@router.post("/search-active-customer-rating-by-get-customer/",
             response_model=Page[schemas.CustomerRatingView])
def search_customer_rating_active_by_get_customer(request: Request, get_customer_id: UUID = Form(...),
                                                  search_text: str = Form(None), db: Session = Depends(get_db),
                                                  current_user: schemas.Users = Depends(
                                                      token_access.get_current_active_user),
                                                  authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer Ratings searched active by get_customer_id - %s", current_user.username,
              get_remote_ip(request))

    customer_list = customer_access.search_customer_rating_active_by_get_customer(db, get_customer_id=get_customer_id,
                                                                                  search_text=search_text)

    if customer_list["status"] != 200:
        log.exception(customer_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=customer_list["status"], detail=customer_list["error_msg"])
    return paginate(customer_list["result"])


# endregion


# region Logs
@router.get("/list-customer-log-by-customer-id/{customer_id}/", response_model=List[schemas.Logs])
def get_customer_log_list_customer_id(request: Request, customer_id: UUID, db: Session = Depends(get_db),
                                      current_user: schemas.Users = Depends(token_access.verify_admin_role),
                                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer Log - %s", current_user.username, get_remote_ip(request))

    db_log = customer_access.get_customer_log_list_customer_id(db, customer_id=customer_id)

    if db_log["status"] != 200:
        raise HTTPException(status_code=db_log["status"], detail=db_log["error_msg"])
    return db_log["result"]


@router.get("/list-customer-balance-log-by-customer-balance-id/{customer_balance_id}/",
            response_model=List[schemas.Logs])
def get_customer_balance_log_list_customer_balance_id(request: Request, customer_balance_id: UUID,
                                                      db: Session = Depends(get_db),
                                                      current_user: schemas.Users = Depends(
                                                          token_access.verify_admin_role),
                                                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Customer Balance Log - %s", current_user.username, get_remote_ip(request))

    db_log = customer_access \
        .get_customer_balance_log_list_customer_balance_id(db, customer_balance_id=customer_balance_id)

    if db_log["status"] != 200:
        raise HTTPException(status_code=db_log["status"], detail=db_log["error_msg"])
    return db_log["result"]


# endregion


add_pagination(router)
