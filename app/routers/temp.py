import logging
from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi_jwt_auth import AuthJWT
from fastapi_pagination import Page, add_pagination, paginate
from sqlalchemy.orm import Session

from app import models, schemas
from app.accesses import temp_access, token_access, user_access, vehicle_access
from app.cruds import temp_crud
from app.database import get_db
from app.lib import get_remote_ip

router = APIRouter()
log = logging.getLogger(__name__)


@router.post("/add-all-data/")
def add_all_data(request: Request, db: Session = Depends(get_db)):
    log.debug("%s - Temp data added - %s", get_remote_ip(request))
    user_access.add_user(db,
                         username="system",
                         password="system",
                         role=models.UserRole.system,
                         image=None,
                         customer_id=None,
                         action_user=None)
    user_access.add_user(db,
                         username="admin",
                         password="admin",
                         role=models.UserRole.admin,
                         image=None,
                         customer_id=None,
                         action_user=None)
    db.commit()
    return True


# region Reports
@router.get("/dashboard-statistics/", response_model=schemas.DashboardStatistics)
def dashboard_statistics(request: Request, db: Session = Depends(get_db),
                         current_user: schemas.Users = Depends(token_access.get_current_active_user),
                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Statistics for dashboard - %s", current_user.username, get_remote_ip(request))

    statistics = temp_access.dashboard_statistics(db)

    if statistics["status"] != 200:
        log.exception(statistics["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=statistics["status"], detail=statistics["error_msg"])
    return statistics["result"]


@router.get("/dashboard-vehicles/", response_model=List[schemas.DashboardVehicles])
def get_vehicle_status_active_list_dashboard(request: Request, db: Session = Depends(get_db),
                                             current_user: schemas.Users = Depends(
                                                 token_access.get_current_active_user),
                                             authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Vehicles for dashboard - %s", current_user.username, get_remote_ip(request))

    statistics = vehicle_access.get_vehicle_status_active_list_dashboard(db)

    if statistics["status"] != 200:
        log.exception(statistics["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=statistics["status"], detail=statistics["error_msg"])
    return statistics["result"]


# endregion


# region Shifts
@router.post("/shift-add/")
def add_shift(request: Request, shift_name: str = Form(...), shift_desc: str = Form(None),
              shift_start_time: str = Form(...), shift_end_time: str = Form(...), db: Session = Depends(get_db),
              current_user: schemas.Users = Depends(token_access.get_current_active_user),
              authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shift added - %s", current_user.username, get_remote_ip(request))

    shift = temp_access.add_shift(db, shift_name=shift_name, shift_desc=shift_desc,
                                  shift_start_time=shift_start_time, shift_end_time=shift_end_time,
                                  action_user=current_user.username)

    if shift["status"] != 200:
        log.exception(shift["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift["status"], detail=shift["error_msg"])
    else:
        db.commit()
    return shift["result"]


@router.put("/shift-edit/")
def edit_shift(request: Request, id: str = Form(...), shift_name: str = Form(...), shift_desc: str = Form(None),
               shift_start_time: str = Form(...), shift_end_time: str = Form(...), db: Session = Depends(get_db),
               current_user: schemas.Users = Depends(token_access.get_current_active_user),
               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shift edited - %s", current_user.username, get_remote_ip(request))

    shift = temp_access.edit_shift(db, id=id, shift_name=shift_name, shift_desc=shift_desc,
                                   shift_start_time=shift_start_time, shift_end_time=shift_end_time,
                                   action_user=current_user.username)

    if shift["status"] != 200:
        log.exception(shift["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift["status"], detail=shift["error_msg"])
    else:
        db.commit()
    return shift["result"]


@router.put("/shift-change-state/{state}/")
def change_shift_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                       db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.get_current_active_user),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shift state changed - %s", current_user.username, get_remote_ip(request))

    shift = temp_access.change_shift_state(db, id=id, state=state, action_user=current_user.username)

    if shift["status"] != 200:
        log.exception(shift["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift["status"], detail=shift["error_msg"])
    else:
        db.commit()
    return shift["result"]


@router.get("/shift-detail/{id}/", response_model=schemas.Shifts)
def get_shift_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                    current_user: schemas.Users = Depends(token_access.get_current_active_user),
                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shift detail get by id - %s", current_user.username, get_remote_ip(request))

    shift = temp_access.get_shift_by_id(db, id=id)

    if shift["status"] != 200:
        log.exception(shift["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift["status"], detail=shift["error_msg"])
    return shift["result"]


@router.get("/shift-list/", response_model=List[schemas.Shifts])
def get_shift_list(request: Request, db: Session = Depends(get_db),
                   current_user: schemas.Users = Depends(token_access.get_current_active_user),
                   authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shifts listed - %s", current_user.username, get_remote_ip(request))

    shift_list = temp_access.get_shift_list(db)

    if shift_list["status"] != 200:
        log.exception(shift_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift_list["status"], detail=shift_list["error_msg"])
    return shift_list["result"]


@router.get("/shift-list-active/", response_model=List[schemas.Shifts])
def get_active_shift_list(request: Request, db: Session = Depends(get_db),
                          current_user: schemas.Users = Depends(token_access.get_current_active_user),
                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shifts listed active - %s", current_user.username, get_remote_ip(request))

    shift_list = temp_access.get_shift_active_list(db)

    if shift_list["status"] != 200:
        log.exception(shift_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift_list["status"], detail=shift_list["error_msg"])
    return shift_list["result"]


@router.post("/shift-search-active/", response_model=Page[schemas.Shifts])
def get_active_shift_search(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
                            current_user: schemas.Users = Depends(token_access.get_current_active_user),
                            authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shifts listed active - %s", current_user.username, get_remote_ip(request))

    shift_list = temp_access.get_active_shift_search(db, search_text)

    if shift_list["status"] != 200:
        log.exception(shift_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift_list["status"], detail=shift_list["error_msg"])
    return paginate(shift_list["result"])


# endregion


# region Shift Vehicles
@router.post("/shift-vehicle-add/")
def add_shift_vehicle(request: Request, shift_id: str = Form(...), vehicle_id: str = Form(None),
                      db: Session = Depends(get_db),
                      current_user: schemas.Users = Depends(token_access.get_current_active_user),
                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shift added - %s", current_user.username, get_remote_ip(request))

    shift_vehicle = temp_access.add_shift_vehicle(db, shift_id=shift_id, vehicle_id=vehicle_id,
                                                  action_user=current_user.username)

    if shift_vehicle["status"] != 200:
        log.exception(shift_vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift_vehicle["status"], detail=shift_vehicle["error_msg"])
    else:
        db.commit()
    return shift_vehicle["result"]


@router.put("/shift-vehicle-change-state/{state}/")
def change_shift_vehicle_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                               db: Session = Depends(get_db),
                               current_user: schemas.Users = Depends(token_access.get_current_active_user),
                               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shift state changed - %s", current_user.username, get_remote_ip(request))

    shift_vehicle = temp_access.change_shift_vehicle_state(db, id=id, state=state, action_user=current_user.username)

    if shift_vehicle["status"] != 200:
        log.exception(shift_vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift_vehicle["status"], detail=shift_vehicle["error_msg"])
    else:
        db.commit()
    return shift_vehicle["result"]


@router.get("/shift-vehicle-detail/{id}/", response_model=schemas.ShiftVehicles)
def get_shift_vehicle_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                            current_user: schemas.Users = Depends(token_access.get_current_active_user),
                            authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shift detail get by id - %s", current_user.username, get_remote_ip(request))

    shift_vehicle = temp_access.get_shift_vehicle_by_id(db, id=id)

    if shift_vehicle["status"] != 200:
        log.exception(shift_vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift_vehicle["status"], detail=shift_vehicle["error_msg"])
    return shift_vehicle["result"]


@router.get("/shift-vehicle-list/", response_model=List[schemas.ShiftVehicles])
def get_shift_vehicle_list(request: Request, db: Session = Depends(get_db),
                           current_user: schemas.Users = Depends(token_access.get_current_active_user),
                           authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shifts listed - %s", current_user.username, get_remote_ip(request))

    shift_vehicle_list = temp_access.get_shift_vehicle_list(db)

    if shift_vehicle_list["status"] != 200:
        log.exception(shift_vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift_vehicle_list["status"], detail=shift_vehicle_list["error_msg"])
    return shift_vehicle_list["result"]


@router.get("/shift-vehicle-list-active/", response_model=List[schemas.ShiftVehicles])
def get_active_shift_vehicle_list(request: Request, db: Session = Depends(get_db),
                                  current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                  authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shifts listed active - %s", current_user.username, get_remote_ip(request))

    shift_vehicle_list = temp_access.get_shift_vehicle_active_list(db)

    if shift_vehicle_list["status"] != 200:
        log.exception(shift_vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift_vehicle_list["status"], detail=shift_vehicle_list["error_msg"])
    return shift_vehicle_list["result"]


@router.post("/shift-vehicle-search-active/", response_model=Page[schemas.ShiftVehicleView])
def get_active_shift_vehicle_search(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
                                    current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shifts listed active - %s", current_user.username, get_remote_ip(request))

    shift_vehicle_list = temp_access.get_active_shift_vehicle_search(db, search_text=search_text)

    if shift_vehicle_list["status"] != 200:
        log.exception(shift_vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift_vehicle_list["status"], detail=shift_vehicle_list["error_msg"])
    return paginate(shift_vehicle_list["result"])


@router.post("/shift-vehicle-search-active-by-shift/", response_model=Page[schemas.ShiftVehicleView])
def get_active_shift_vehicle_search_by_shift(request: Request, search_text: str = Form(None),
                                             shift_id: UUID = Form(...), db: Session = Depends(get_db),
                                             current_user: schemas.Users = Depends(
                                                 token_access.get_current_active_user),
                                             authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shifts listed active - %s", current_user.username, get_remote_ip(request))

    shift_vehicle_list = temp_access.get_active_shift_vehicle_search_by_shift(db, search_text=search_text,
                                                                              shift_id=shift_id)

    if shift_vehicle_list["status"] != 200:
        log.exception(shift_vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=shift_vehicle_list["status"], detail=shift_vehicle_list["error_msg"])
    return paginate(shift_vehicle_list["result"])


# endregion


# region Services
@router.post("/service-add/")
def add_service(request: Request, service_name_tm: str = Form(...), service_name_ru: str = Form(None),
                service_name_en: str = Form(None), service_desc_tm: str = Form(None),
                service_desc_ru: str = Form(None), service_desc_en: str = Form(None),
                service_priority: int = Form(...), db: Session = Depends(get_db),
                current_user: schemas.Users = Depends(token_access.verify_admin_role),
                authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Service added - %s", current_user.username, get_remote_ip(request))

    service = temp_access.add_service(db, service_name_tm=service_name_tm, service_name_ru=service_name_ru,
                                      service_name_en=service_name_en, service_desc_tm=service_desc_tm,
                                      service_desc_ru=service_desc_ru, service_desc_en=service_desc_en,
                                      service_priority=service_priority, action_user=current_user.username)

    if service["status"] != 200:
        log.exception(service["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service["status"], detail=service["error_msg"])
    else:
        db.commit()
    return service["result"]


@router.put("/service-edit/")
def edit_service(request: Request, id: UUID = Form(...), service_name_tm: str = Form(...),
                 service_name_ru: str = Form(None), service_name_en: str = Form(None),
                 service_desc_tm: str = Form(None), service_desc_ru: str = Form(None),
                 service_desc_en: str = Form(None), service_priority: int = Form(...),
                 db: Session = Depends(get_db), current_user: schemas.Users = Depends(token_access.verify_admin_role),
                 authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Service edited - %s", current_user.username, get_remote_ip(request))

    service = temp_access.edit_service(db, id=id, service_name_tm=service_name_tm, service_name_ru=service_name_ru,
                                       service_name_en=service_name_en, service_desc_tm=service_desc_tm,
                                       service_desc_ru=service_desc_ru, service_desc_en=service_desc_en,
                                       service_priority=service_priority, action_user=current_user.username)

    if service["status"] != 200:
        log.exception(service["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service["status"], detail=service["error_msg"])
    else:
        db.commit()
    return service["result"]


@router.put("/service-change-state/{state}/")
def change_service_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                         db: Session = Depends(get_db),
                         current_user: schemas.Users = Depends(token_access.verify_admin_role),
                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Service state changed - %s", current_user.username, get_remote_ip(request))

    service = temp_access.change_service_state(db, id=id, state=state, action_user=current_user.username)

    if service["status"] != 200:
        log.exception(service["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service["status"], detail=service["error_msg"])
    else:
        db.commit()
    return service["result"]


@router.get("/service-detail/{id}/", response_model=schemas.Services)
def get_service_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                      current_user: schemas.Users = Depends(token_access.verify_admin_role),
                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Service detail get by id - %s", current_user.username, get_remote_ip(request))

    service = temp_access.get_service_by_id(db, id=id)

    if service["status"] != 200:
        log.exception(service["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service["status"], detail=service["error_msg"])
    return service["result"]


@router.get("/service-list/", response_model=List[schemas.Services])
def get_service_list(request: Request, db: Session = Depends(get_db),
                     current_user: schemas.Users = Depends(token_access.verify_admin_role),
                     authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Services listed - %s", current_user.username, get_remote_ip(request))

    service_list = temp_access.get_service_list(db)

    if service_list["status"] != 200:
        log.exception(service_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service_list["status"], detail=service_list["error_msg"])
    return service_list["result"]


@router.get("/service-list-active/", response_model=List[schemas.Services])
def get_active_service_list(request: Request, db: Session = Depends(get_db),
                            current_user: schemas.Users = Depends(token_access.get_current_active_user),
                            authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Services listed active - %s", current_user.username, get_remote_ip(request))

    service_list = temp_access.get_service_active_list(db)

    if service_list["status"] != 200:
        log.exception(service_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service_list["status"], detail=service_list["error_msg"])
    return service_list["result"]


@router.post("/service-search-active/", response_model=Page[schemas.Services])
def get_active_service_search(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
                              current_user: schemas.Users = Depends(token_access.get_current_active_user),
                              authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Services searched active - %s", current_user.username, get_remote_ip(request))

    service_list = temp_access.get_active_service_search(db, search_text)

    if service_list["status"] != 200:
        log.exception(service_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service_list["status"], detail=service_list["error_msg"])
    return paginate(service_list["result"])


# endregion


# region Shift Vehicles
@router.post("/service-vehicle-add/")
def add_service_vehicle(request: Request, service_id: str = Form(...), vehicle_id: str = Form(None),
                        db: Session = Depends(get_db),
                        current_user: schemas.Users = Depends(token_access.get_current_active_user),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shift added - %s", current_user.username, get_remote_ip(request))

    service_vehicle = temp_access.add_service_vehicle(db, service_id=service_id, vehicle_id=vehicle_id,
                                                      action_user=current_user.username)

    if service_vehicle["status"] != 200:
        log.exception(service_vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service_vehicle["status"], detail=service_vehicle["error_msg"])
    else:
        db.commit()
    return service_vehicle["result"]


@router.put("/service-vehicle-change-state/{state}/")
def change_service_vehicle_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                                 db: Session = Depends(get_db),
                                 current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                 authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shift state changed - %s", current_user.username, get_remote_ip(request))

    service_vehicle = temp_access.change_service_vehicle_state(db, id=id, state=state,
                                                               action_user=current_user.username)

    if service_vehicle["status"] != 200:
        log.exception(service_vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service_vehicle["status"], detail=service_vehicle["error_msg"])
    else:
        db.commit()
    return service_vehicle["result"]


@router.get("/service-vehicle-detail/{id}/", response_model=schemas.ServiceVehicles)
def get_service_vehicle_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                              current_user: schemas.Users = Depends(token_access.get_current_active_user),
                              authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shift detail get by id - %s", current_user.username, get_remote_ip(request))

    service_vehicle = temp_access.get_service_vehicle_by_id(db, id=id)

    if service_vehicle["status"] != 200:
        log.exception(service_vehicle["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service_vehicle["status"], detail=service_vehicle["error_msg"])
    return service_vehicle["result"]


@router.get("/service-vehicle-list/", response_model=List[schemas.ServiceVehicles])
def get_service_vehicle_list(request: Request, db: Session = Depends(get_db),
                             current_user: schemas.Users = Depends(token_access.get_current_active_user),
                             authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shifts listed - %s", current_user.username, get_remote_ip(request))

    service_vehicle_list = temp_access.get_service_vehicle_list(db)

    if service_vehicle_list["status"] != 200:
        log.exception(service_vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service_vehicle_list["status"], detail=service_vehicle_list["error_msg"])
    return service_vehicle_list["result"]


@router.get("/service-vehicle-list-active/", response_model=List[schemas.ServiceVehicles])
def get_active_service_vehicle_list(request: Request, db: Session = Depends(get_db),
                                    current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shifts listed active - %s", current_user.username, get_remote_ip(request))

    service_vehicle_list = temp_access.get_service_vehicle_active_list(db)

    if service_vehicle_list["status"] != 200:
        log.exception(service_vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service_vehicle_list["status"], detail=service_vehicle_list["error_msg"])
    return service_vehicle_list["result"]


@router.post("/service-vehicle-search-active/", response_model=Page[schemas.ServiceVehicleView])
def get_active_service_vehicle_search(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
                                      current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shifts listed active - %s", current_user.username, get_remote_ip(request))

    service_vehicle_list = temp_access.get_active_service_vehicle_search(db, search_text)

    if service_vehicle_list["status"] != 200:
        log.exception(service_vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service_vehicle_list["status"], detail=service_vehicle_list["error_msg"])
    return paginate(service_vehicle_list["result"])


@router.post("/service-vehicle-search-active-by-service/", response_model=Page[schemas.ServiceVehicleView])
def get_active_service_vehicle_search_by_service(request: Request, search_text: str = Form(None),
                                                 service_id: UUID = Form(...), db: Session = Depends(get_db),
                                                 current_user: schemas.Users = Depends(
                                                     token_access.get_current_active_user),
                                                 authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Shifts listed active - %s", current_user.username, get_remote_ip(request))

    service_vehicle_list = temp_access.get_active_service_vehicle_search_by_service(db, search_text=search_text,
                                                                                    service_id=service_id)

    if service_vehicle_list["status"] != 200:
        log.exception(service_vehicle_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=service_vehicle_list["status"], detail=service_vehicle_list["error_msg"])
    return paginate(service_vehicle_list["result"])


# endregion


# region Districts
@router.post("/district-add/")
def add_district(request: Request, district_name_tm: str = Form(...), district_name_ru: str = Form(None),
                 district_name_en: str = Form(None), district_desc_tm: str = Form(None),
                 district_desc_ru: str = Form(None), district_desc_en: str = Form(None),
                 district_geo: str = Form(...), db: Session = Depends(get_db),
                 current_user: schemas.Users = Depends(token_access.verify_admin_role),
                 authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - District added - %s", current_user.username, get_remote_ip(request))

    district = temp_access.add_district(db, district_name_tm=district_name_tm, district_name_ru=district_name_ru,
                                        district_name_en=district_name_en, district_desc_tm=district_desc_tm,
                                        district_desc_ru=district_desc_ru, district_desc_en=district_desc_en,
                                        district_geo=district_geo, action_user=current_user.username)

    if district["status"] != 200:
        log.exception(district["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=district["status"], detail=district["error_msg"])
    else:
        db.commit()
    return district["result"]


@router.put("/district-edit/")
def edit_district(request: Request, id: UUID = Form(...), district_name_tm: str = Form(...),
                  district_name_ru: str = Form(None), district_name_en: str = Form(None),
                  district_desc_tm: str = Form(None), district_desc_ru: str = Form(None),
                  district_desc_en: str = Form(None), district_geo: str = Form(...),
                  db: Session = Depends(get_db), current_user: schemas.Users = Depends(token_access.verify_admin_role),
                  authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - District edited - %s", current_user.username, get_remote_ip(request))

    district = temp_access.edit_district(db, id=id, district_name_tm=district_name_tm,
                                         district_name_ru=district_name_ru,
                                         district_name_en=district_name_en, district_desc_tm=district_desc_tm,
                                         district_desc_ru=district_desc_ru, district_desc_en=district_desc_en,
                                         district_geo=district_geo, action_user=current_user.username)

    if district["status"] != 200:
        log.exception(district["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=district["status"], detail=district["error_msg"])
    else:
        db.commit()
    return district["result"]


@router.put("/district-change-state/{state}/")
def change_district_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                          db: Session = Depends(get_db),
                          current_user: schemas.Users = Depends(token_access.verify_admin_role),
                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - District state changed - %s", current_user.username, get_remote_ip(request))

    district = temp_access.change_district_state(db, id=id, state=state, action_user=current_user.username)

    if district["status"] != 200:
        log.exception(district["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=district["status"], detail=district["error_msg"])
    else:
        db.commit()
    return district["result"]


@router.get("/district-detail/{id}/", response_model=schemas.Districts)
def get_district_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.verify_admin_role),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - District detail get by id - %s", current_user.username, get_remote_ip(request))

    district = temp_access.get_district_by_id(db, id=id)

    if district["status"] != 200:
        log.exception(district["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=district["status"], detail=district["error_msg"])
    return district["result"]


@router.get("/district-list/", response_model=List[schemas.Districts])
def get_district_list(request: Request, db: Session = Depends(get_db),
                      current_user: schemas.Users = Depends(token_access.verify_admin_role),
                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Districts listed - %s", current_user.username, get_remote_ip(request))

    district_list = temp_access.get_district_list(db)

    if district_list["status"] != 200:
        log.exception(district_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=district_list["status"], detail=district_list["error_msg"])
    return district_list["result"]


@router.get("/district-list-active/", response_model=List[schemas.Districts])
def get_active_district_list(request: Request, db: Session = Depends(get_db),
                             current_user: schemas.Users = Depends(token_access.get_current_active_user),
                             authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Districts listed active - %s", current_user.username, get_remote_ip(request))

    district_list = temp_access.get_district_active_list(db)

    if district_list["status"] != 200:
        log.exception(district_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=district_list["status"], detail=district_list["error_msg"])
    return district_list["result"]


@router.get("/district-list-active-no-id/{id}/", response_model=List[schemas.Districts])
def get_district_active_list_no_id(request: Request, id: UUID, db: Session = Depends(get_db),
                                   current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                   authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Districts listed active - %s", current_user.username, get_remote_ip(request))

    district_list = temp_access.get_district_active_list_no_id(db, id=id)

    if district_list["status"] != 200:
        log.exception(district_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=district_list["status"], detail=district_list["error_msg"])
    return district_list["result"]


@router.get("/district-list-active-with-drivers/", response_model=List[schemas.DistrictDrivers])
def get_district_active_list_with_drivers(request: Request, db: Session = Depends(get_db),
                                          current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Districts listed active with drivers - %s", current_user.username, get_remote_ip(request))

    district_list = temp_access.get_district_active_list_with_drivers(db)

    if district_list["status"] != 200:
        log.exception(district_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=district_list["status"], detail=district_list["error_msg"])
    return district_list["result"]


@router.post("/district-search-active/", response_model=Page[schemas.Districts])
def get_active_district_search(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
                               current_user: schemas.Users = Depends(token_access.get_current_active_user),
                               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Districts searched active - %s", current_user.username, get_remote_ip(request))

    district_list = temp_access.get_active_district_search(db, search_text)

    if district_list["status"] != 200:
        log.exception(district_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=district_list["status"], detail=district_list["error_msg"])
    return paginate(district_list["result"])


@router.post("/district-driver-order/")
def get_district_driver(request: Request, driver_id: UUID = Form(...), district_id: UUID = Form(...),
                        db: Session = Depends(get_db),
                        current_user: schemas.Users = Depends(token_access.get_current_active_user),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - District driver order - %s", current_user.username, get_remote_ip(request))

    district_list = temp_access.get_district_driver(db, driver_id=driver_id, district_id=district_id)

    if district_list["status"] != 200:
        log.exception(district_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=district_list["status"], detail=district_list["error_msg"])
    return district_list["result"]


# endregion


# region Rates
@router.post("/rate-add/")
def add_rate(request: Request, rate_name: str = Form(...), rate_desc: str = Form(None), service_id: str = Form(None),
             shift_id: str = Form(None), district_ids: str = Form(None), start_date: str = Form(None),
             end_date: str = Form(None), price_km: float = Form(...), price_min: float = Form(...),
             price_wait_min: float = Form(...), minute_free_wait: float = Form(...), km_free: float = Form(...),
             price_delivery: float = Form(...), minute_for_wait: float = Form(...), price_cancel: float = Form(...),
             price_minimal: float = Form(...), service_prc: float = Form(...), birthday_discount_prc: float = Form(...),
             db: Session = Depends(get_db), current_user: schemas.Users = Depends(token_access.verify_admin_role),
             authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Rate added - %s", current_user.username, get_remote_ip(request))

    rate = temp_access.add_rate(db, rate_name=rate_name, rate_desc=rate_desc, service_id=service_id, shift_id=shift_id,
                                district_ids=district_ids, start_date=start_date, end_date=end_date, price_km=price_km,
                                price_min=price_min, price_wait_min=price_wait_min, minute_free_wait=minute_free_wait,
                                price_delivery=price_delivery, minute_for_wait=minute_for_wait, km_free=km_free,
                                price_cancel=price_cancel, price_minimal=price_minimal, service_prc=service_prc,
                                birthday_discount_prc=birthday_discount_prc, action_user=current_user.username)

    if rate["status"] != 200:
        log.exception(rate["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=rate["status"], detail=rate["error_msg"])
    else:
        db.commit()
    return rate["result"]


@router.put("/rate-edit/")
def edit_rate(request: Request, id: UUID = Form(...), rate_name: str = Form(...), rate_desc: str = Form(None),
              service_id: str = Form(None), shift_id: str = Form(None), district_ids: str = Form(None),
              start_date: str = Form(None), end_date: str = Form(None), price_km: float = Form(...),
              price_min: float = Form(...), minute_free_wait: float = Form(...), price_delivery: float = Form(...),
              minute_for_wait: float = Form(...), price_cancel: float = Form(...), price_minimal: float = Form(...),
              service_prc: float = Form(...), birthday_discount_prc: float = Form(...), db: Session = Depends(get_db),
              current_user: schemas.Users = Depends(token_access.verify_admin_role), authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Rate edited - %s", current_user.username, get_remote_ip(request))

    rate = temp_access.edit_rate(db, id=id, rate_name=rate_name, rate_desc=rate_desc, service_id=service_id,
                                 shift_id=shift_id, district_ids=district_ids, start_date=start_date, end_date=end_date,
                                 price_km=price_km, price_min=price_min, minute_free_wait=minute_free_wait,
                                 price_delivery=price_delivery, minute_for_wait=minute_for_wait,
                                 price_cancel=price_cancel, price_minimal=price_minimal, service_prc=service_prc,
                                 birthday_discount_prc=birthday_discount_prc, action_user=current_user.username)

    if rate["status"] != 200:
        log.exception(rate["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=rate["status"], detail=rate["error_msg"])
    else:
        db.commit()
    return rate["result"]


@router.put("/rate-change-state/{state}/")
def change_rate_state(request: Request, state: models.EntityState, id: UUID = Form(...),
                      db: Session = Depends(get_db),
                      current_user: schemas.Users = Depends(token_access.verify_admin_role),
                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Rate state changed - %s", current_user.username, get_remote_ip(request))

    rate = temp_access.change_rate_state(db, id=id, state=state, action_user=current_user.username)

    if rate["status"] != 200:
        log.exception(rate["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=rate["status"], detail=rate["error_msg"])
    else:
        db.commit()
    return rate["result"]


@router.get("/rate-detail/{id}/", response_model=schemas.Rates)
def get_rate_by_id(request: Request, id: UUID, db: Session = Depends(get_db),
                   current_user: schemas.Users = Depends(token_access.verify_admin_role),
                   authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Rate detail get by id - %s", current_user.username, get_remote_ip(request))

    rate = temp_access.get_rate_by_id(db, id=id)

    if rate["status"] != 200:
        log.exception(rate["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=rate["status"], detail=rate["error_msg"])
    return rate["result"]


@router.get("/rate-detail-by-info/{service_id}/{district_id}/{order_date}/", response_model=schemas.Rates)
def get_rate_by_info(request: Request, service_id: UUID, district_id: str, order_date: datetime,
                     db: Session = Depends(get_db),
                     current_user: schemas.Users = Depends(token_access.get_current_active_user),
                     authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Rate detail get by info - %s", current_user.username, get_remote_ip(request))

    rate = temp_access.get_rate_by_info(db, service_id=service_id, district_id=district_id, order_date=order_date)

    if rate["status"] != 200:
        log.exception(rate["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=rate["status"], detail=rate["error_msg"])
    return rate["result"]


@router.get("/rate-list/", response_model=List[schemas.Rates])
def get_rate_list(request: Request, db: Session = Depends(get_db),
                  current_user: schemas.Users = Depends(token_access.verify_admin_role),
                  authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Rates listed - %s", current_user.username, get_remote_ip(request))

    rate_list = temp_access.get_rate_list(db)

    if rate_list["status"] != 200:
        log.exception(rate_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=rate_list["status"], detail=rate_list["error_msg"])
    return rate_list["result"]


@router.get("/rate-list-active/", response_model=List[schemas.Rates])
def get_active_rate_list(request: Request, db: Session = Depends(get_db),
                         current_user: schemas.Users = Depends(token_access.get_current_active_user),
                         authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Rates listed active - %s", current_user.username, get_remote_ip(request))

    rate_list = temp_access.get_rate_active_list(db)

    if rate_list["status"] != 200:
        log.exception(rate_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=rate_list["status"], detail=rate_list["error_msg"])
    return rate_list["result"]


@router.get("/rate-list-active-by-info/{district_id}/{order_date}/", response_model=List[schemas.RateView2])
def get_active_rate_list_by_info(request: Request, district_id: str, order_date: datetime,
                                 db: Session = Depends(get_db),
                                 current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                 authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Rates listed active by info - %s", current_user.username, get_remote_ip(request))

    rate_list = temp_access.get_active_rate_list_by_info(db, district_id=district_id, order_date=order_date)

    if rate_list["status"] != 200:
        log.exception(rate_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=rate_list["status"], detail=rate_list["error_msg"])
    return rate_list["result"]


@router.post("/rate-list-active-by-geo-info/{district_id}/{order_date}/", response_model=List[schemas.RateView2])
def get_active_rate_list_by_geo_info(request: Request, district_id: str, order_date: datetime,
                                     latitude_from: float = Form(...), longitude_from: float = Form(...),
                                     latitude_to: float = Form(...), longitude_to: float = Form(...),
                                     db: Session = Depends(get_db),
                                     current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                     authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Rates listed active by info - %s", current_user.username, get_remote_ip(request))

    rate_list = temp_access.get_active_rate_list_by_geo_info(db, district_id=district_id, order_date=order_date,
                                                             latitude_from=latitude_from,
                                                             longitude_from=longitude_from,
                                                             latitude_to=latitude_to,
                                                             longitude_to=longitude_to)

    if rate_list["status"] != 200:
        log.exception(rate_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=rate_list["status"], detail=rate_list["error_msg"])
    return rate_list["result"]


@router.get("/rate-list-view-active/", response_model=List[schemas.RateView])
def get_rate_active_list_view(request: Request, db: Session = Depends(get_db),
                              current_user: schemas.Users = Depends(token_access.get_current_active_user),
                              authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Rates listed active view - %s", current_user.username, get_remote_ip(request))

    rate_list = temp_access.get_rate_active_list_view(db)

    if rate_list["status"] != 200:
        log.exception(rate_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=rate_list["status"], detail=rate_list["error_msg"])
    return rate_list["result"]


@router.post("/rate-search-active/", response_model=Page[schemas.RateView])
def get_active_rate_search(request: Request, search_text: str = Form(None), db: Session = Depends(get_db),
                           current_user: schemas.Users = Depends(token_access.get_current_active_user),
                           authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Rates searched active - %s", current_user.username, get_remote_ip(request))

    rate_list = temp_access.get_active_rate_search(db, search_text)

    if rate_list["status"] != 200:
        log.exception(rate_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=rate_list["status"], detail=rate_list["error_msg"])
    return paginate(rate_list["result"])


# endregion


add_pagination(router)
