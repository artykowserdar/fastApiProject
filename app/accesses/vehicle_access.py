import logging

from geoalchemy2.shape import to_shape
from shapely import wkt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import FlushError

from app import models
from app.accesses import geo_access
from app.cruds import vehicle_crud, temp_crud, order_crud, customer_crud
from app.routers import websocket

log = logging.getLogger(__name__)


# region Vehicle Models
def add_model(db: Session, model_name, model_desc, action_user):
    try:
        status = 200
        error_msg = ''
        db_model = vehicle_crud.add_model(db, model_name, model_desc, action_user)
        if db_model is None:
            status = 418
            error_msg = 'add_model_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_model = None
        error_msg = 'add_model_error'
    return {"status": status, "error_msg": error_msg, "result": db_model}


def edit_model(db: Session, id, model_name, model_desc, action_user):
    try:
        db_model = get_model_by_id(db, id)
        status = db_model["status"]
        error_msg = db_model["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_model["result"]}
        db_model = vehicle_crud.edit_model(db, id, model_name, model_desc, action_user)
        if db_model is None:
            status = 418
            error_msg = 'edit_model_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_model = None
        error_msg = 'edit_model_error'
    return {"status": status, "error_msg": error_msg, "result": db_model}


def change_model_state(db: Session, id, state, action_user):
    try:
        db_model = get_model_by_id(db, id)
        status = db_model["status"]
        error_msg = db_model["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_model["result"]}
        db_model = vehicle_crud.change_model_state(db, id, state, action_user)
        if db_model is None:
            status = 418
            error_msg = 'change_model_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_model = None
        error_msg = 'change_model_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_model}


def get_model_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_model = vehicle_crud.get_model_by_id(db, id)
        if db_model is None:
            status = 418
            error_msg = 'get_model_detail_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_model = None
        error_msg = 'get_model_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_model}


def get_model_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_model = vehicle_crud.get_model_list(db)
        if db_model is None:
            status = 418
            error_msg = 'get_model_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_model = None
        error_msg = 'get_model_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_model}


def get_model_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_model = vehicle_crud.get_model_active_list(db)
        if db_model is None:
            status = 418
            error_msg = 'get_model_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_model = None
        error_msg = 'get_model_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_model}


def get_active_model_search(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_model = vehicle_crud.get_active_model_search(db, search_text)
        if db_model is None:
            status = 418
            error_msg = 'get_model_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_model = None
        error_msg = 'get_model_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_model}


# endregion


# region Vehicle Colors
def add_color(db: Session, color_name, color_desc, action_user):
    try:
        status = 200
        error_msg = ''
        db_color = vehicle_crud.add_color(db, color_name, color_desc, action_user)
        if db_color is None:
            status = 418
            error_msg = 'add_color_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_color = None
        error_msg = 'add_color_error'
    return {"status": status, "error_msg": error_msg, "result": db_color}


def edit_color(db: Session, id, color_name, color_desc, action_user):
    try:
        db_color = get_color_by_id(db, id)
        status = db_color["status"]
        error_msg = db_color["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_color["result"]}
        db_color = vehicle_crud.edit_color(db, id, color_name, color_desc, action_user)
        if db_color is None:
            status = 418
            error_msg = 'edit_color_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_color = None
        error_msg = 'edit_color_error'
    return {"status": status, "error_msg": error_msg, "result": db_color}


def change_color_state(db: Session, id, state, action_user):
    try:
        db_color = get_color_by_id(db, id)
        status = db_color["status"]
        error_msg = db_color["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_color["result"]}
        db_color = vehicle_crud.change_color_state(db, id, state, action_user)
        if db_color is None:
            status = 418
            error_msg = 'change_color_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_color = None
        error_msg = 'change_color_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_color}


def get_color_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_color = vehicle_crud.get_color_by_id(db, id)
        if db_color is None:
            status = 418
            error_msg = 'get_color_detail_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_color = None
        error_msg = 'get_color_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_color}


def get_color_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_color = vehicle_crud.get_color_list(db)
        if db_color is None:
            status = 418
            error_msg = 'get_color_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_color = None
        error_msg = 'get_color_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_color}


def get_color_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_color = vehicle_crud.get_color_active_list(db)
        if db_color is None:
            status = 418
            error_msg = 'get_color_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_color = None
        error_msg = 'get_color_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_color}


def get_active_color_search(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_color = vehicle_crud.get_active_color_search(db, search_text)
        if db_color is None:
            status = 418
            error_msg = 'get_color_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_color = None
        error_msg = 'get_color_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_color}


# endregion


# region Vehicle Types
def add_type(db: Session, type_name, type_desc, action_user):
    try:
        status = 200
        error_msg = ''
        db_type = vehicle_crud.add_type(db, type_name, type_desc, action_user)
        if db_type is None:
            status = 418
            error_msg = 'add_type_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_type = None
        error_msg = 'add_type_error'
    return {"status": status, "error_msg": error_msg, "result": db_type}


def edit_type(db: Session, id, type_name, type_desc, action_user):
    try:
        db_type = get_type_by_id(db, id)
        status = db_type["status"]
        error_msg = db_type["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_type["result"]}
        db_type = vehicle_crud.edit_type(db, id, type_name, type_desc, action_user)
        if db_type is None:
            status = 418
            error_msg = 'edit_type_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_type = None
        error_msg = 'edit_type_error'
    return {"status": status, "error_msg": error_msg, "result": db_type}


def change_type_state(db: Session, id, state, action_user):
    try:
        db_type = get_type_by_id(db, id)
        status = db_type["status"]
        error_msg = db_type["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_type["result"]}
        db_type = vehicle_crud.change_type_state(db, id, state, action_user)
        if db_type is None:
            status = 418
            error_msg = 'change_type_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_type = None
        error_msg = 'change_type_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_type}


def get_type_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_type = vehicle_crud.get_type_by_id(db, id)
        if db_type is None:
            status = 418
            error_msg = 'get_type_detail_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_type = None
        error_msg = 'get_type_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_type}


def get_type_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_type = vehicle_crud.get_type_list(db)
        if db_type is None:
            status = 418
            error_msg = 'get_type_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_type = None
        error_msg = 'get_type_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_type}


def get_type_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_type = vehicle_crud.get_type_active_list(db)
        if db_type is None:
            status = 418
            error_msg = 'get_type_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_type = None
        error_msg = 'get_type_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_type}


def get_active_type_search(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_type = vehicle_crud.get_active_type_search(db, search_text)
        if db_type is None:
            status = 418
            error_msg = 'get_type_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_type = None
        error_msg = 'get_type_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_type}


# endregion


# region Vehicles
def add_vehicle(db: Session, model_id, type_id, document_no, vehicle_no, vehicle_year, vehicle_color,
                engine_no, body_no, max_weight, net_weight, validity, vehicle_desc, driver_id, action_user):
    try:
        if vehicle_crud.get_vehicle_by_no(db, vehicle_no) is None:
            status = 200
            error_msg = ''
            db_color = vehicle_crud.get_color_by_id(db, vehicle_color)
            db_model = vehicle_crud.get_model_by_id(db, model_id)
            vehicle_color = db_color.color_name
            vehicle_name = {"tm": db_model.model_name["tm"] + ' ' + vehicle_no,
                            "ru": db_model.model_name["ru"] + ' ' + vehicle_no,
                            "en": db_model.model_name["en"] + ' ' + vehicle_no}
            db_vehicle = vehicle_crud.add_vehicle(db, model_id, type_id, vehicle_name, document_no, vehicle_no,
                                                  vehicle_year, vehicle_color, engine_no, body_no, max_weight,
                                                  net_weight, validity, vehicle_desc, driver_id, action_user)
            if db_vehicle is None:
                status = 418
                error_msg = 'add_vehicle_failed'
        else:
            status = 418
            db_vehicle = None
            error_msg = 'vehicle_conflict'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_vehicle = None
        error_msg = 'add_vehicle_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def edit_vehicle(db: Session, id, model_id, type_id, document_no, vehicle_no, vehicle_year, vehicle_color,
                 engine_no, body_no, max_weight, net_weight, validity, vehicle_desc, action_user):
    try:
        if vehicle_crud.get_vehicle_by_no_with_id(db, id, vehicle_no) is None:
            status = 200
            error_msg = ''
            db_color = vehicle_crud.get_color_by_id(db, vehicle_color)
            db_model = vehicle_crud.get_model_by_id(db, model_id)
            vehicle_color = db_color.color_name
            vehicle_name = {"tm": db_model.model_name["tm"] + ' ' + vehicle_no,
                            "ru": db_model.model_name["ru"] + ' ' + vehicle_no,
                            "en": db_model.model_name["en"] + ' ' + vehicle_no}
            db_vehicle = vehicle_crud.edit_vehicle(db, id, model_id, type_id, vehicle_name, document_no, vehicle_no,
                                                   vehicle_year, vehicle_color, engine_no, body_no, max_weight,
                                                   net_weight, validity, vehicle_desc, action_user)
            if db_vehicle is None:
                status = 418
                error_msg = 'add_vehicle_failed'
        else:
            status = 418
            db_vehicle = None
            error_msg = 'vehicle_conflict'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_vehicle = None
        error_msg = 'edit_vehicle_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def edit_vehicle_driver(db: Session, id, driver_id, action_user):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.edit_vehicle_driver(db, id, driver_id, action_user)
        if db_vehicle is None:
            status = 418
            error_msg = 'add_vehicle_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_vehicle = None
        error_msg = 'edit_vehicle_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def change_vehicle_state(db: Session, id, state, action_user):
    try:
        db_vehicle = get_vehicle_by_id(db, id)
        status = db_vehicle["status"]
        error_msg = db_vehicle["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_vehicle["result"]}
        db_vehicle = vehicle_crud.change_vehicle_state(db, id, state, action_user)
        if db_vehicle is None:
            status = 418
            error_msg = 'change_vehicle_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_vehicle = None
        error_msg = 'change_vehicle_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_by_id(db, id)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_detail_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_list(db)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_active_list(db)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_active_list_no_driver(db: Session):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_active_list_no_driver(db)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_active_list_no_driver_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_active_list_no_driver_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_active_list_no_shift(db: Session, shift_id):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_active_list_no_shift(db, shift_id)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_active_list_no_shift_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_active_list_no_shift_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_active_list_no_service(db: Session, service_id):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_active_list_no_service(db, service_id)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_active_list_no_service_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_active_list_no_service_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_active_list_by_driver(db: Session, driver_id):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_active_list_by_driver(db, driver_id)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_active_list_by_driver_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_active_list_by_driver_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_list_view(db: Session):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_list_view(db)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_list_view_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_list_view_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_active_list_view(db: Session):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_active_list_view(db)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_active_list_view_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_active_list_view_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_active_list_view_by_driver(db: Session, driver_id):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_active_list_view_by_driver(db, driver_id)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_active_list_view_by_driver_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_active_list_view_by_driver_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_active_list_view_available(db: Session):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_active_list_view_available(db)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_active_list_view_available_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_active_list_view_available_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_active_list_view_active(db: Session):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_active_list_view_active(db)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_active_list_view_active_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_active_list_view_active_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def get_vehicle_active_list_view_active_driver(db: Session, driver_id):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_active_list_view_active_driver(db, driver_id)
        if db_vehicle is None:
            status = 418
            error_msg = 'get_vehicle_active_list_view_active_driver_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'get_vehicle_active_list_view_active_driver_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def search_vehicle_active(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_vehicle = vehicle_crud.search_vehicle_active(db, search_text)
        if db_vehicle is None:
            status = 418
            error_msg = 'search_vehicle_active_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'search_vehicle_active_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def search_vehicle_active_by_type(db: Session, search_text, type_id):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_vehicle = vehicle_crud.search_vehicle_active_by_type(db, search_text, type_id)
        if db_vehicle is None:
            status = 418
            error_msg = 'search_vehicle_active_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'search_vehicle_active_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def search_vehicle_active_by_service(db: Session, search_text, service_id):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_vehicle = vehicle_crud.search_vehicle_active_by_service(db, search_text, service_id)
        if db_vehicle is None:
            status = 418
            error_msg = 'search_vehicle_active_by_service_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'search_vehicle_active_by_service_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def search_vehicle_active_by_service_available(db: Session, search_text, service_id):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_vehicle = vehicle_crud.search_vehicle_active_by_service_available(db, search_text, service_id)
        if db_vehicle is None:
            status = 418
            error_msg = 'search_vehicle_active_by_service_available_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'search_vehicle_active_by_service_available_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


def search_vehicle_active_by_driver(db: Session, search_text, driver_id):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_vehicle = vehicle_crud.search_vehicle_active_by_driver(db, search_text, driver_id)
        if db_vehicle is None:
            status = 418
            error_msg = 'search_vehicle_active_by_driver_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_vehicle = None
        error_msg = 'search_vehicle_active_by_driver_error'
    return {"status": status, "error_msg": error_msg, "result": db_vehicle}


# endregion


# region Vehicle Status
async def online_vehicle_status(db: Session, driver_id, vehicle_id, latitude, longitude, action_user):
    try:
        status = 200
        error_msg = ''
        db_driver = customer_crud.get_customer_balance_by_customer_minimum(db, driver_id)
        if db_driver:
            district_id = None
            order_id = None
            vehicle_available = models.VehicleAvailable.free
            order_data = order_crud.get_order_new_by_driver(db, driver_id, vehicle_id)
            if latitude and longitude:
                db_district = geo_access.get_district_by_coordinates(db, latitude, longitude)
                if db_district["result"]:
                    district_id = db_district["result"]["district_id"]
                geo_location = f"POINT({latitude} {longitude})"
                if order_data:
                    order_id = order_data.id
                vehicle_crud.add_driver_vehicle_location(db, driver_id, vehicle_id, order_id, geo_location, district_id)
            service_ids = []
            db_service = temp_crud.get_service_vehicle_active_list_by_vehicle(db, vehicle_id)
            if db_service:
                for service in db_service:
                    service_ids.append(service.service_id)
            db_vehicle_status = vehicle_crud.get_vehicle_status_by_info(db, driver_id, vehicle_id)
            if db_vehicle_status:
                if order_data:
                    vehicle_available = models.VehicleAvailable.busy
                db_status = vehicle_crud.edit_vehicle_status_by_id(db, db_vehicle_status.id, service_ids, district_id,
                                                                   vehicle_available, models.VehicleState.active)
                if db_status is None:
                    status = 418
                    error_msg = 'edit_vehicle_status_failed'
            else:
                db_status = vehicle_crud.add_vehicle_status(db, driver_id, vehicle_id, service_ids, district_id)
                if db_status is None:
                    status = 418
                    error_msg = 'add_vehicle_status_failed'
            db.commit()
            await websocket.dashboard_statistics(db)
            await websocket.dashboard_vehicles(db)
        else:
            status = 409
            db_status = None
            error_msg = 'balance_reached_minimum'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_status = None
        error_msg = 'online_vehicle_status_error'
    return {"status": status, "error_msg": error_msg, "result": db_status}


def activate_vehicle_status(db: Session, driver_id, vehicle_id, action_user):
    try:
        status = 200
        error_msg = ''
        db_status = vehicle_crud.change_vehicle_status_state(db, driver_id, vehicle_id, models.VehicleState.active)
        if db_status is None:
            status = 418
            error_msg = 'activate_vehicle_status_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_status = None
        error_msg = 'activate_vehicle_status_error'
    return {"status": status, "error_msg": error_msg, "result": db_status}


async def disable_vehicle_status(db: Session, driver_id, vehicle_id, action_user):
    try:
        status = 200
        error_msg = ''
        db_status = vehicle_crud.change_vehicle_status_state(db, driver_id, vehicle_id, models.VehicleState.disable)
        if db_status is None:
            status = 418
            error_msg = 'disable_vehicle_status_failed'
        db.commit()
        await websocket.dashboard_statistics(db)
        await websocket.dashboard_vehicles(db)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_status = None
        error_msg = 'disable_vehicle_status_error'
    return {"status": status, "error_msg": error_msg, "result": db_status}


async def disable_vehicle_status_vehicle(db: Session, vehicle_id, action_user):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_by_id_simple(db, vehicle_id)
        db_status = vehicle_crud.change_vehicle_status_state(db, db_vehicle.driver_id, vehicle_id,
                                                             models.VehicleState.disable)
        if db_status is None:
            status = 418
            error_msg = 'disable_vehicle_status_failed'
        db.commit()
        await websocket.dashboard_statistics(db)
        await websocket.dashboard_vehicles(db)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_status = None
        error_msg = 'disable_vehicle_status_error'
    return {"status": status, "error_msg": error_msg, "result": db_status}


def free_vehicle_status(db: Session, driver_id, vehicle_id, action_user):
    try:
        status = 200
        error_msg = ''
        db_status = vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id,
                                                                 models.VehicleAvailable.free)
        if db_status is None:
            status = 418
            error_msg = 'free_vehicle_status_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_status = None
        error_msg = 'free_vehicle_status_error'
    return {"status": status, "error_msg": error_msg, "result": db_status}


def busy_vehicle_status(db: Session, driver_id, vehicle_id, action_user):
    try:
        status = 200
        error_msg = ''
        db_status = vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id,
                                                                 models.VehicleAvailable.busy)
        if db_status is None:
            status = 418
            error_msg = 'busy_vehicle_status_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_status = None
        error_msg = 'busy_vehicle_status_error'
    return {"status": status, "error_msg": error_msg, "result": db_status}


def get_vehicle_status_active_list_view(db: Session):
    try:
        status = 200
        error_msg = ''
        db_status = vehicle_crud.get_vehicle_status_active_list_view(db)
        if db_status is None:
            status = 418
            error_msg = 'get_vehicle_status_active_list_view_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_status = None
        error_msg = 'get_vehicle_status_active_list_view_error'
    return {"status": status, "error_msg": error_msg, "result": db_status}


def get_vehicle_status_active_list_dashboard(db: Session):
    try:
        status = 200
        error_msg = ''
        result = []
        db_status = vehicle_crud.get_vehicle_status_active_list_view(db)
        if db_status is None:
            status = 418
            error_msg = 'get_vehicle_status_active_list_view_failed'
        for data in db_status:
            geo_location = data.geo_location
            shapely_geometry = to_shape(geo_location)
            wkt_representation = shapely_geometry.wkt
            point = wkt.loads(wkt_representation)
            coordinates = list(point.coords[0])
            result.append({
                "driver_id": str(data.driver_id),
                "vehicle_id": str(data.vehicle_id),
                "geo_location": coordinates,
                "vehicle_available": data.vehicle_available.name,
                "vehicle_name": data.vehicle_name,
                "fullname": data.fullname
            })
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        result = None
        error_msg = 'get_vehicle_status_active_list_view_error'
    return {"status": status, "error_msg": error_msg, "result": result}

# endregion
