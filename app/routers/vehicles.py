import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.orm import Session

from app import models, schemas
from app.accesses import vehicle_access, token_access
from app.database import get_db
from app.lib import get_remote_ip

router = APIRouter()
log = logging.getLogger(__name__)


# region Vehicle Models
@router.post("/model-add/")
def add_model(request: Request, model_name: str = Form(...), model_desc: str = Form(None),
              db: Session = Depends(get_db), current_user: schemas.Users = Depends(token_access.verify_admin_role),
              authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Model added - %s", current_user.username, get_remote_ip(request))

    model = vehicle_access.add_model(db, model_name=model_name, model_desc=model_desc,
                                     action_user=current_user.username)

    if model["status"] != 200:
        log.exception(model["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=model["status"], detail=model["error_msg"])
    else:
        db.commit()
    return model["result"]


@router.put("/model-edit/")
def edit_model(request: Request, id: UUID = Form(...), model_name: str = Form(...), model_desc: str = Form(None),
               db: Session = Depends(get_db), current_user: schemas.Users = Depends(token_access.verify_admin_role),
               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Model edited - %s", current_user.username, get_remote_ip(request))

    model = vehicle_access.edit_model(db, id=id, model_name=model_name, model_desc=model_desc,
                                      action_user=current_user.username)

    if model["status"] != 200:
        log.exception(model["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=model["status"], detail=model["error_msg"])
    else:
        db.commit()
    return model["result"]


@router.put("/model-change-state/{state}/")
def change_model_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                       db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.verify_admin_role),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Model state changed - %s", current_user.username, get_remote_ip(request))

    model = vehicle_access.change_model_state(db, id=id, state=state, action_user=current_user.username)

    if model["status"] != 200:
        log.exception(model["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=model["status"], detail=model["error_msg"])
    else:
        db.commit()
    return model["result"]


@router.get("/model-detail/{id}/", response_model=schemas.VehicleModels)
def get_model_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                    current_user: schemas.Users = Depends(token_access.verify_admin_role),
                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Model detail get by id - %s", current_user.username, get_remote_ip(request))

    model = vehicle_access.get_model_by_id(db, id=id)

    if model["status"] != 200:
        log.exception(model["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=model["status"], detail=model["error_msg"])
    return model["result"]


@router.get("/model-list/", response_model=List[schemas.VehicleModels])
def get_model_list(request: Request, db: Session = Depends(get_db),
                   current_user: schemas.Users = Depends(token_access.verify_admin_role),
                   authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Models listed - %s", current_user.username, get_remote_ip(request))

    model_list = vehicle_access.get_model_list(db)

    if model_list["status"] != 200:
        log.exception(model_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=model_list["status"], detail=model_list["error_msg"])
    return model_list["result"]


@router.get("/model-list-active/", response_model=List[schemas.VehicleModels])
def get_active_model_list(request: Request, db: Session = Depends(get_db),
                          current_user: schemas.Users = Depends(token_access.get_current_active_user),
                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Models listed active - %s", current_user.username, get_remote_ip(request))

    model_list = vehicle_access.get_model_active_list(db)

    if model_list["status"] != 200:
        log.exception(model_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=model_list["status"], detail=model_list["error_msg"])
    return model_list["result"]


@router.post("/model-search-active/", response_model=Page[schemas.VehicleModels])
def get_active_model_search(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
                            current_user: schemas.Users = Depends(token_access.get_current_active_user),
                            authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - VehicleModels searched active - %s", current_user.username, get_remote_ip(request))

    model_list = vehicle_access.get_active_model_search(db, search_text)

    if model_list["status"] != 200:
        log.exception(model_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=model_list["status"], detail=model_list["error_msg"])
    return paginate(model_list["result"])


# endregion


# region Vehicle Colors
@router.post("/color-add/")
def add_color(request: Request, color_name: str = Form(...), color_desc: str = Form(None),
              db: Session = Depends(get_db), current_user: schemas.Users = Depends(token_access.verify_admin_role),
              authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Color added - %s", current_user.username, get_remote_ip(request))

    color = vehicle_access.add_color(db, color_name=color_name, color_desc=color_desc,
                                     action_user=current_user.username)

    if color["status"] != 200:
        log.exception(color["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=color["status"], detail=color["error_msg"])
    else:
        db.commit()
    return color["result"]


@router.put("/color-edit/")
def edit_color(request: Request, id: UUID = Form(...), color_name: str = Form(...), color_desc: str = Form(None),
               db: Session = Depends(get_db), current_user: schemas.Users = Depends(token_access.verify_admin_role),
               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Color edited - %s", current_user.username, get_remote_ip(request))

    color = vehicle_access.edit_color(db, id=id, color_name=color_name, color_desc=color_desc,
                                      action_user=current_user.username)

    if color["status"] != 200:
        log.exception(color["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=color["status"], detail=color["error_msg"])
    else:
        db.commit()
    return color["result"]


@router.put("/color-change-state/{state}/")
def change_color_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                       db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.verify_admin_role),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Color state changed - %s", current_user.username, get_remote_ip(request))

    color = vehicle_access.change_color_state(db, id=id, state=state, action_user=current_user.username)

    if color["status"] != 200:
        log.exception(color["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=color["status"], detail=color["error_msg"])
    else:
        db.commit()
    return color["result"]


@router.get("/color-detail/{id}/", response_model=schemas.VehicleColors)
def get_color_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                    current_user: schemas.Users = Depends(token_access.verify_admin_role),
                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Color detail get by id - %s", current_user.username, get_remote_ip(request))

    color = vehicle_access.get_color_by_id(db, id=id)

    if color["status"] != 200:
        log.exception(color["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=color["status"], detail=color["error_msg"])
    return color["result"]


@router.get("/color-list/", response_model=List[schemas.VehicleColors])
def get_color_list(request: Request, db: Session = Depends(get_db),
                   current_user: schemas.Users = Depends(token_access.verify_admin_role),
                   authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Colors listed - %s", current_user.username, get_remote_ip(request))

    color_list = vehicle_access.get_color_list(db)

    if color_list["status"] != 200:
        log.exception(color_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=color_list["status"], detail=color_list["error_msg"])
    return color_list["result"]


@router.get("/color-list-active/", response_model=List[schemas.VehicleColors])
def get_active_color_list(request: Request, db: Session = Depends(get_db),
                          current_user: schemas.Users = Depends(token_access.get_current_active_user),
                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Colors listed active - %s", current_user.username, get_remote_ip(request))

    color_list = vehicle_access.get_color_active_list(db)

    if color_list["status"] != 200:
        log.exception(color_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=color_list["status"], detail=color_list["error_msg"])
    return color_list["result"]


@router.post("/color-search-active/", response_model=Page[schemas.VehicleColors])
def get_active_color_search(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
                            current_user: schemas.Users = Depends(token_access.get_current_active_user),
                            authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - VehicleColors searched active - %s", current_user.username, get_remote_ip(request))

    color_list = vehicle_access.get_active_color_search(db, search_text)

    if color_list["status"] != 200:
        log.exception(color_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=color_list["status"], detail=color_list["error_msg"])
    return paginate(color_list["result"])


# endregion


# region Vehicle Types
@router.post("/type-add/")
def add_type(request: Request, type_name: str = Form(...), type_desc: str = Form(None),
             db: Session = Depends(get_db), current_user: schemas.Users = Depends(token_access.verify_admin_role),
             authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Type added - %s", current_user.username, get_remote_ip(request))

    type = vehicle_access.add_type(db, type_name=type_name, type_desc=type_desc, action_user=current_user.username)

    if type["status"] != 200:
        log.exception(type["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=type["status"], detail=type["error_msg"])
    else:
        db.commit()
    return type["result"]


@router.put("/type-edit/")
def edit_type(request: Request, id: UUID = Form(...), type_name: str = Form(...), type_desc: str = Form(None),
              db: Session = Depends(get_db), current_user: schemas.Users = Depends(token_access.verify_admin_role),
              authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Type edited - %s", current_user.username, get_remote_ip(request))

    type = vehicle_access.edit_type(db, id=id, type_name=type_name, type_desc=type_desc,
                                    action_user=current_user.username)

    if type["status"] != 200:
        log.exception(type["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=type["status"], detail=type["error_msg"])
    else:
        db.commit()
    return type["result"]


@router.put("/type-change-state/{state}/")
def change_type_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                      db: Session = Depends(get_db),
                      current_user: schemas.Users = Depends(token_access.verify_admin_role),
                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Type state changed - %s", current_user.username, get_remote_ip(request))

    type = vehicle_access.change_type_state(db, id=id, state=state, action_user=current_user.username)

    if type["status"] != 200:
        log.exception(type["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=type["status"], detail=type["error_msg"])
    else:
        db.commit()
    return type["result"]


@router.get("/type-detail/{id}/", response_model=schemas.VehicleTypes)
def get_type_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                   current_user: schemas.Users = Depends(token_access.verify_admin_role),
                   authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Type detail get by id - %s", current_user.username, get_remote_ip(request))

    type = vehicle_access.get_type_by_id(db, id=id)

    if type["status"] != 200:
        log.exception(type["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=type["status"], detail=type["error_msg"])
    return type["result"]


@router.get("/type-list/", response_model=List[schemas.VehicleTypes])
def get_type_list(request: Request, db: Session = Depends(get_db),
                  current_user: schemas.Users = Depends(token_access.verify_admin_role),
                  authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Types listed - %s", current_user.username, get_remote_ip(request))

    type_list = vehicle_access.get_type_list(db)

    if type_list["status"] != 200:
        log.exception(type_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=type_list["status"], detail=type_list["error_msg"])
    return type_list["result"]


@router.get("/type-list-active/", response_model=List[schemas.VehicleTypes])
def get_active_type_list(request: Request, db: Session = Depends(get_db),
                         current_user: schemas.Users = Depends(token_access.get_current_active_user),
                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Types listed active - %s", current_user.username, get_remote_ip(request))

    type_list = vehicle_access.get_type_active_list(db)

    if type_list["status"] != 200:
        log.exception(type_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=type_list["status"], detail=type_list["error_msg"])
    return type_list["result"]


@router.post("/type-search-active/", response_model=Page[schemas.VehicleTypes])
def get_active_type_search(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
                           current_user: schemas.Users = Depends(token_access.get_current_active_user),
                           authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - VehicleTypes searched active - %s", current_user.username, get_remote_ip(request))

    type_list = vehicle_access.get_active_type_search(db, search_text)

    if type_list["status"] != 200:
        log.exception(type_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=type_list["status"], detail=type_list["error_msg"])
    return paginate(type_list["result"])


# endregion


# region Vehicles
@router.post("/vehicle-add/")
def add_vehicle(request: Request, model_id: str = Form(...), type_id: str = Form(...), vehicle_color: str = Form(...),
                vehicle_no: str = Form(...), vehicle_year: int = Form(None), document_no: str = Form(None),
                engine_no: str = Form(None), body_no: str = Form(None), max_weight: str = Form(None),
                net_weight: str = Form(None), validity: str = Form(None), vehicle_desc: str = Form(None),
                driver_id: str = Form(None), db: Session = Depends(get_db),
                current_user: schemas.Users = Depends(token_access.verify_admin_role), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle added - %s", current_user.username, get_remote_ip(request))

    vehicle = vehicle_access.add_vehicle(db, model_id=model_id, type_id=type_id, document_no=document_no,
                                         vehicle_no=vehicle_no, vehicle_year=vehicle_year,
                                         vehicle_color=vehicle_color, engine_no=engine_no, body_no=body_no,
                                         max_weight=max_weight, net_weight=net_weight, validity=validity,
                                         vehicle_desc=vehicle_desc, driver_id=driver_id,
                                         action_user=current_user.username)

    if vehicle["status"] != 200:
        log.exception(vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle["status"], detail=vehicle["error_msg"])
    else:
        db.commit()
    return vehicle["result"]


@router.put("/vehicle-edit/")
def edit_vehicle(request: Request, id: UUID = Form(...), model_id: str = Form(...), type_id: str = Form(...),
                 vehicle_color: str = Form(...), vehicle_no: str = Form(...), vehicle_year: int = Form(None),
                 document_no: str = Form(None), engine_no: str = Form(None), body_no: str = Form(None),
                 max_weight: str = Form(None), net_weight: str = Form(None), validity: str = Form(None),
                 vehicle_desc: str = Form(None), db: Session = Depends(get_db),
                 current_user: schemas.Users = Depends(token_access.verify_admin_role),
                 authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle edited - %s", current_user.username, get_remote_ip(request))

    vehicle = vehicle_access.edit_vehicle(db, id=id, model_id=model_id, type_id=type_id, document_no=document_no,
                                          vehicle_no=vehicle_no, vehicle_year=vehicle_year,
                                          vehicle_color=vehicle_color, engine_no=engine_no, body_no=body_no,
                                          max_weight=max_weight, net_weight=net_weight, validity=validity,
                                          vehicle_desc=vehicle_desc, action_user=current_user.username)

    if vehicle["status"] != 200:
        log.exception(vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle["status"], detail=vehicle["error_msg"])
    else:
        db.commit()
    return vehicle["result"]


@router.put("/vehicle-edit-driver/")
def edit_vehicle_driver(request: Request, id: str = Form(...), driver_id: str = Form(None),
                        db: Session = Depends(get_db),
                        current_user: schemas.Users = Depends(token_access.verify_admin_role),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle edited - %s", current_user.username, get_remote_ip(request))

    vehicle = vehicle_access.edit_vehicle_driver(db, id=id, driver_id=driver_id, action_user=current_user.username)

    if vehicle["status"] != 200:
        log.exception(vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle["status"], detail=vehicle["error_msg"])
    else:
        db.commit()
    return vehicle["result"]


@router.put("/vehicle-change-state/{state}/")
def change_vehicle_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                         db: Session = Depends(get_db),
                         current_user: schemas.Users = Depends(token_access.verify_admin_role),
                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle state changed - %s", current_user.username, get_remote_ip(request))

    vehicle = vehicle_access.change_vehicle_state(db, id=id, state=state, action_user=current_user.username)

    if vehicle["status"] != 200:
        log.exception(vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle["status"], detail=vehicle["error_msg"])
    else:
        db.commit()
    return vehicle["result"]


@router.get("/vehicle-detail/{id}/", response_model=schemas.VehicleView)
def get_vehicle_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                      current_user: schemas.Users = Depends(token_access.get_current_active_user),
                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle detail get by id - %s", current_user.username, get_remote_ip(request))

    vehicle = vehicle_access.get_vehicle_by_id(db, id=id)

    if vehicle["status"] != 200:
        log.exception(vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle["status"], detail=vehicle["error_msg"])
    return vehicle["result"]


@router.get("/vehicle-list/", response_model=List[schemas.Vehicles])
def get_vehicle_list(request: Request, db: Session = Depends(get_db),
                     current_user: schemas.Users = Depends(token_access.verify_admin_role),
                     authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles listed - %s", current_user.username, get_remote_ip(request))

    vehicle_list = vehicle_access.get_vehicle_list(db)

    if vehicle_list["status"] != 200:
        log.exception(vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list["status"], detail=vehicle_list["error_msg"])
    return vehicle_list["result"]


@router.get("/vehicle-list-active/", response_model=List[schemas.Vehicles])
def get_active_vehicle_list(request: Request, db: Session = Depends(get_db),
                            current_user: schemas.Users = Depends(token_access.get_current_active_user),
                            authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles listed active - %s", current_user.username, get_remote_ip(request))

    vehicle_list = vehicle_access.get_vehicle_active_list(db)

    if vehicle_list["status"] != 200:
        log.exception(vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list["status"], detail=vehicle_list["error_msg"])
    return vehicle_list["result"]


@router.get("/vehicle-list-active-no-driver/", response_model=List[schemas.Vehicles])
def get_vehicle_active_list_no_driver(request: Request, db: Session = Depends(get_db),
                                      current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles listed active no drivers - %s", current_user.username, get_remote_ip(request))

    vehicle_list = vehicle_access.get_vehicle_active_list_no_driver(db)

    if vehicle_list["status"] != 200:
        log.exception(vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list["status"], detail=vehicle_list["error_msg"])
    return vehicle_list["result"]


@router.get("/vehicle-list-active-no-shift/{shift_id}/", response_model=List[schemas.Vehicles])
def get_vehicle_active_list_no_shift(request: Request, shift_id: UUID, db: Session = Depends(get_db),
                                     current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                     authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles listed active no shift - %s", current_user.username, get_remote_ip(request))

    vehicle_list = vehicle_access.get_vehicle_active_list_no_shift(db, shift_id=shift_id)

    if vehicle_list["status"] != 200:
        log.exception(vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list["status"], detail=vehicle_list["error_msg"])
    return vehicle_list["result"]


@router.get("/vehicle-list-active-no-service/{service_id}/", response_model=List[schemas.VehicleView])
def get_vehicle_active_list_no_service(request: Request, service_id: UUID, db: Session = Depends(get_db),
                                       current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles listed active no service - %s", current_user.username, get_remote_ip(request))

    vehicle_list = vehicle_access.get_vehicle_active_list_no_service(db, service_id=service_id)

    if vehicle_list["status"] != 200:
        log.exception(vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list["status"], detail=vehicle_list["error_msg"])
    return vehicle_list["result"]


@router.get("/vehicle-list-active-by-driver/{driver_id}/", response_model=List[schemas.Vehicles])
def get_vehicle_active_list_by_driver(request: Request, driver_id: UUID, db: Session = Depends(get_db),
                                      current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles listed active by driver - %s", current_user.username, get_remote_ip(request))

    vehicle_list = vehicle_access.get_vehicle_active_list_by_driver(db, driver_id=driver_id)

    if vehicle_list["status"] != 200:
        log.exception(vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list["status"], detail=vehicle_list["error_msg"])
    return vehicle_list["result"]


@router.get("/vehicle-list-view/", response_model=List[schemas.VehicleView])
def get_vehicle_list_view(request: Request, db: Session = Depends(get_db),
                          current_user: schemas.Users = Depends(token_access.verify_admin_role),
                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles listed - %s", current_user.username, get_remote_ip(request))

    vehicle_list_view = vehicle_access.get_vehicle_list_view(db)

    if vehicle_list_view["status"] != 200:
        log.exception(vehicle_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list_view["status"], detail=vehicle_list_view["error_msg"])
    return vehicle_list_view["result"]


@router.get("/vehicle-list-view-active/", response_model=List[schemas.VehicleView])
def get_active_vehicle_list_view(request: Request, db: Session = Depends(get_db),
                                 current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                 authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles listed active - %s", current_user.username, get_remote_ip(request))

    vehicle_list_view = vehicle_access.get_vehicle_active_list_view(db)

    if vehicle_list_view["status"] != 200:
        log.exception(vehicle_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list_view["status"], detail=vehicle_list_view["error_msg"])
    return vehicle_list_view["result"]


@router.get("/vehicle-list-view-active-by-driver/{driver_id}/", response_model=List[schemas.VehicleView])
def get_vehicle_active_list_view_by_driver(request: Request, driver_id: UUID, db: Session = Depends(get_db),
                                           current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                           authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles listed active by driver - %s", current_user.username, get_remote_ip(request))

    vehicle_list = vehicle_access.get_vehicle_active_list_view_by_driver(db, driver_id=driver_id)

    if vehicle_list["status"] != 200:
        log.exception(vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list["status"], detail=vehicle_list["error_msg"])
    return vehicle_list["result"]


@router.get("/vehicle-list-view-active-available/", response_model=List[schemas.VehicleView])
def get_vehicle_active_list_view_available(request: Request, db: Session = Depends(get_db),
                                           current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                           authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles listed active available - %s", current_user.username, get_remote_ip(request))

    vehicle_list_view = vehicle_access.get_vehicle_active_list_view_available(db)

    if vehicle_list_view["status"] != 200:
        log.exception(vehicle_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list_view["status"], detail=vehicle_list_view["error_msg"])
    return vehicle_list_view["result"]


@router.get("/vehicle-list-view-active-active/", response_model=List[schemas.VehicleView])
def get_vehicle_active_list_view_active(request: Request, db: Session = Depends(get_db),
                                        current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles listed active available - %s", current_user.username, get_remote_ip(request))

    vehicle_list_view = vehicle_access.get_vehicle_active_list_view_active(db)

    if vehicle_list_view["status"] != 200:
        log.exception(vehicle_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list_view["status"], detail=vehicle_list_view["error_msg"])
    return vehicle_list_view["result"]


@router.get("/vehicle-list-view-active-driver/{driver_id}/", response_model=List[schemas.VehicleView])
def get_vehicle_active_list_view_active_driver(request: Request, driver_id: UUID, db: Session = Depends(get_db),
                                               current_user: schemas.Users = Depends(
                                                   token_access.get_current_active_user),
                                               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles listed active available - %s", current_user.username, get_remote_ip(request))

    vehicle_list_view = vehicle_access.get_vehicle_active_list_view_active_driver(db, driver_id=driver_id)

    if vehicle_list_view["status"] != 200:
        log.exception(vehicle_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list_view["status"], detail=vehicle_list_view["error_msg"])
    return vehicle_list_view["result"]


@router.post("/vehicle-search-active/", response_model=Page[schemas.VehicleView])
def search_vehicle_active(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
                          current_user: schemas.Users = Depends(token_access.get_current_active_user),
                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles searched active - %s", current_user.username, get_remote_ip(request))

    vehicle_list_view = vehicle_access.search_vehicle_active(db, search_text=search_text)

    if vehicle_list_view["status"] != 200:
        log.exception(vehicle_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list_view["status"], detail=vehicle_list_view["error_msg"])
    return paginate(vehicle_list_view["result"])


@router.post("/vehicle-search-active-by-type/", response_model=Page[schemas.VehicleView])
def search_vehicle_active_by_type(request: Request, search_text: str = Form(None), type_id: str = Form(None),
                                  db: Session = Depends(get_db),
                                  current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                  authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles searched active - %s", current_user.username, get_remote_ip(request))

    vehicle_list_view = vehicle_access.search_vehicle_active_by_type(db, search_text=search_text, type_id=type_id)

    if vehicle_list_view["status"] != 200:
        log.exception(vehicle_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list_view["status"], detail=vehicle_list_view["error_msg"])
    return paginate(vehicle_list_view["result"])


@router.post("/vehicle-search-active-by-service/", response_model=Page[schemas.VehicleView])
def search_vehicle_active_by_service(request: Request, search_text: str = Form(None), service_id: str = Form(None),
                                     db: Session = Depends(get_db),
                                     current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                     authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles searched active - %s", current_user.username, get_remote_ip(request))

    vehicle_list_view = vehicle_access.search_vehicle_active_by_service(db, search_text=search_text,
                                                                        service_id=service_id)

    if vehicle_list_view["status"] != 200:
        log.exception(vehicle_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list_view["status"], detail=vehicle_list_view["error_msg"])
    return paginate(vehicle_list_view["result"])


@router.post("/vehicle-search-active-by-service-available/", response_model=Page[schemas.VehicleView])
def search_vehicle_active_by_service_available(request: Request, search_text: str = Form(None),
                                               service_id: str = Form(None),
                                               db: Session = Depends(get_db),
                                               current_user: schemas.Users = Depends(
                                                   token_access.get_current_active_user),
                                               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles searched active - %s", current_user.username, get_remote_ip(request))

    vehicle_list_view = vehicle_access.search_vehicle_active_by_service_available(db, search_text=search_text,
                                                                                  service_id=service_id)

    if vehicle_list_view["status"] != 200:
        log.exception(vehicle_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list_view["status"], detail=vehicle_list_view["error_msg"])
    return paginate(vehicle_list_view["result"])


@router.post("/vehicle-search-active-by-driver/", response_model=List[schemas.VehicleView])
def search_vehicle_active_by_driver(request: Request, search_text: str = Form(None), driver_id: UUID = Form(...),
                                    db: Session = Depends(get_db),
                                    current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles searched active - %s", current_user.username, get_remote_ip(request))

    vehicle_list_view = vehicle_access.search_vehicle_active_by_driver(db, search_text=search_text, driver_id=driver_id)

    if vehicle_list_view["status"] != 200:
        log.exception(vehicle_list_view["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle_list_view["status"], detail=vehicle_list_view["error_msg"])
    return vehicle_list_view["result"]


# endregion


# region Vehicle Status
@router.post("/vehicle-status-online/")
async def online_vehicle_status(request: Request, driver_id: UUID = Form(...), vehicle_id: UUID = Form(...),
                                latitude: float = Form(None), longitude: float = Form(None),
                                db: Session = Depends(get_db),
                                current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Status set online - %s", current_user.username, get_remote_ip(request))

    vehicle = await vehicle_access.online_vehicle_status(db, driver_id=driver_id, vehicle_id=vehicle_id,
                                                         latitude=latitude, longitude=longitude,
                                                         action_user=current_user.username)

    if vehicle["status"] != 200:
        log.exception(vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle["status"], detail=vehicle["error_msg"])
    else:
        db.commit()
    return vehicle["result"]


@router.put("/vehicle-status-activate/")
def activate_vehicle_status(request: Request, driver_id: UUID = Form(...), vehicle_id: UUID = Form(...),
                            db: Session = Depends(get_db),
                            current_user: schemas.Users = Depends(token_access.get_current_active_user),
                            authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Status set activate - %s", current_user.username, get_remote_ip(request))

    vehicle = vehicle_access.activate_vehicle_status(db, driver_id=driver_id, vehicle_id=vehicle_id,
                                                     action_user=current_user.username)

    if vehicle["status"] != 200:
        log.exception(vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle["status"], detail=vehicle["error_msg"])
    else:
        db.commit()
    return vehicle["result"]


@router.put("/vehicle-status-disable/")
async def disable_vehicle_status(request: Request, driver_id: UUID = Form(...), vehicle_id: UUID = Form(...),
                                 db: Session = Depends(get_db),
                                 current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                 authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Status set disable - %s", current_user.username, get_remote_ip(request))

    vehicle = await vehicle_access.disable_vehicle_status(db, driver_id=driver_id, vehicle_id=vehicle_id,
                                                          action_user=current_user.username)

    if vehicle["status"] != 200:
        log.exception(vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle["status"], detail=vehicle["error_msg"])
    else:
        db.commit()
    return vehicle["result"]


@router.put("/vehicle-status-disable-vehicle/")
async def disable_vehicle_status_vehicle(request: Request, vehicle_id: UUID = Form(...),
                                         db: Session = Depends(get_db),
                                         current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Status set disable - %s", current_user.username, get_remote_ip(request))

    vehicle = await vehicle_access.disable_vehicle_status_vehicle(db, vehicle_id=vehicle_id,
                                                                  action_user=current_user.username)

    if vehicle["status"] != 200:
        log.exception(vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle["status"], detail=vehicle["error_msg"])
    else:
        db.commit()
    return vehicle["result"]


@router.put("/vehicle-status-free/")
def free_vehicle_status(request: Request, driver_id: UUID = Form(...), vehicle_id: UUID = Form(...),
                        db: Session = Depends(get_db),
                        current_user: schemas.Users = Depends(token_access.get_current_active_user),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Status set free - %s", current_user.username, get_remote_ip(request))

    vehicle = vehicle_access.free_vehicle_status(db, driver_id=driver_id, vehicle_id=vehicle_id,
                                                 action_user=current_user.username)

    if vehicle["status"] != 200:
        log.exception(vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle["status"], detail=vehicle["error_msg"])
    else:
        db.commit()
    return vehicle["result"]


@router.put("/vehicle-status-busy/")
def busy_vehicle_status(request: Request, driver_id: UUID = Form(...), vehicle_id: UUID = Form(...),
                        db: Session = Depends(get_db),
                        current_user: schemas.Users = Depends(token_access.verify_admin_role),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicle Status set busy - %s", current_user.username, get_remote_ip(request))

    vehicle = vehicle_access.busy_vehicle_status(db, driver_id=driver_id, vehicle_id=vehicle_id,
                                                 action_user=current_user.username)

    if vehicle["status"] != 200:
        log.exception(vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=vehicle["status"], detail=vehicle["error_msg"])
    else:
        db.commit()
    return vehicle["result"]


# endregion


add_pagination(router)
