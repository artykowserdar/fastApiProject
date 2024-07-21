import json
import logging
import math
import os
import random
import string

from geopy.distance import geodesic
from shapely.geometry import Polygon
from shapely import wkb
from datetime import date, datetime, timedelta

from PIL import Image
from num2words import num2words
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import FlushError

from app import models
from app.cruds import temp_crud, order_crud, vehicle_crud

log = logging.getLogger(__name__)


# region Functions
def create_image(image, image_name, static_path):
    status = 200
    error_msg = ''
    try:
        if image:
            target_tmb = static_path + '/tmb'
            if not os.path.exists(target_tmb):
                os.makedirs(target_tmb)

            target_image = static_path
            if not os.path.exists(target_image):
                os.makedirs(target_image)

            if image_name != 'no-image':
                os.remove(static_path + '/' + image_name)
            ext = os.path.splitext(image.filename)[-1]
            imagename = ''.join(random.choices(string.ascii_letters + string.digits, k=16)) + ext
            destination_tmb = "/".join([target_tmb, imagename])
            destination_image = "/".join([target_image, imagename])

            with open(destination_image, 'wb+') as f:
                f.write(image.file.read())
                f.close()

            with Image.open(destination_image) as real_size_img:
                real_size_img.save(destination_image, 'JPEG')

            with Image.open(destination_image) as thumb:
                thumb = thumb.convert('RGB')
                thumb = thumb.resize((150, 150), Image.LANCZOS)
                thumb.save(destination_tmb, 'JPEG', quality=90)
        elif image != '' and image_name != 'no-image':
            imagename = ''
            destination_image = ''
        else:
            imagename = 'no-image'
            destination_image = 'no-image'
        result = {"imagename": imagename, "destination_image": destination_image}
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        result = None
        error_msg = 'create_image_error'
    return {"status": status, "error_msg": error_msg, "result": result}


def create_file(file, static_path):
    try:
        status = 200
        error_msg = ''
        target_file = static_path
        if not os.path.exists(target_file):
            os.makedirs(target_file)
        ext = os.path.splitext(file.filename)[-1]
        filename = ''.join(random.choices(string.ascii_letters + string.digits, k=16)) + ext
        destination_file = "/".join([target_file, filename])

        with open(destination_file, 'wb+') as f:
            f.write(file.file.read())
            f.close()
        result = {"filename": filename, "destination_file": destination_file}
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        result = None
        error_msg = 'create_file_error'
    return {"status": status, "error_msg": error_msg, "result": result}


def num2ru(num_to_convert):
    text = num2words(int(num_to_convert), lang='ru')
    num_to_convert = round(num_to_convert, 2)
    decimal = str(format((num_to_convert - int(num_to_convert)), '.2f')).split('.')[1]

    return text + " манат " + decimal + " тенге"


def date_of_week(date_now, day):
    r = date.fromisocalendar(date_now.year, date_now.isocalendar()[1], day)
    return r


def create_employee_code(employee_type):
    if employee_type == models.EmployeeType.admin:
        employee_code = 'ADM-' + ''.join(random.choice('0123456789ABCDEF') for _ in range(8))
    elif employee_type == models.EmployeeType.boss:
        employee_code = 'BSS-' + ''.join(random.choice('0123456789ABCDEF') for _ in range(8))
    elif employee_type == models.EmployeeType.operator:
        employee_code = 'OPR-' + ''.join(random.choice('0123456789ABCDEF') for _ in range(8))
    elif employee_type == models.EmployeeType.driver:
        employee_code = 'DRV-' + ''.join(random.choice('0123456789ABCDEF') for _ in range(8))
    else:
        employee_code = 'UNK-' + ''.join(random.choice('0123456789ABCDEF') for _ in range(8))

    return employee_code


def create_order_code():
    order_code = 'ORD-' + ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(8))

    return order_code


def create_user_password():
    password = ''.join(random.choice('0123456789') for _ in range(6))

    return password


def create_user_code(customer_type):
    if customer_type == models.CustomerType.client:
        customer = 'CLT-'
    else:
        customer = 'EMP-'
    user_code = customer + ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(8))

    return user_code


def create_payment_code():
    payment_code = 'PAY-' + ''.join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(8))

    return payment_code


# endregion


# region Reports
def dashboard_statistics(db: Session):
    try:
        status = 200
        error_msg = ''
        today = datetime.now()
        yesterday = datetime.now() - timedelta(days=1)
        standart_orders = order_crud.count_orders_standart(db, today)
        postponed_orders = order_crud.count_orders_postponed(db, today)
        standart_orders_1 = order_crud.count_orders_standart(db, yesterday)
        postponed_orders_1 = order_crud.count_orders_postponed(db, yesterday)
        waiting_orders = order_crud.count_orders_waiting(db)
        active_vehicles = vehicle_crud.count_vehicles_active(db)
        free_vehicles = vehicle_crud.count_vehicles_free(db)
        result = {"standart_orders": standart_orders,
                  "standart_orders_1": standart_orders_1,
                  "postponed_orders": postponed_orders,
                  "postponed_orders_1": postponed_orders_1,
                  "waiting_orders": waiting_orders,
                  "active_vehicles": active_vehicles,
                  "free_vehicles": free_vehicles,
                  "json_type": "dashboard_statistics"}
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        result = None
        error_msg = 'get_service_vehicle_list_error'
    return {"status": status, "error_msg": error_msg, "result": result}


# endregion


# region Shift
def add_shift(db: Session, shift_name, shift_desc, shift_start_time, shift_end_time, action_user):
    try:
        status = 200
        error_msg = ''
        shift_start_date = str(datetime.now().date()) + " " + shift_start_time
        shift_end_date = str(datetime.now().date()) + " " + shift_end_time
        db_shift = temp_crud.add_shift(db, shift_name, shift_desc, shift_start_date, shift_end_date, action_user)
        if db_shift is None:
            status = 418
            error_msg = 'add_shift_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_shift = None
        error_msg = 'add_shift_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift}


def edit_shift(db: Session, id, shift_name, shift_desc, shift_start_time, shift_end_time, action_user):
    try:
        db_shift = get_shift_by_id(db, id)
        status = db_shift["status"]
        error_msg = db_shift["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_shift["result"]}
        shift_start_date = str(datetime.now().date()) + " " + shift_start_time
        shift_end_date = str(datetime.now().date()) + " " + shift_end_time
        db_shift = temp_crud.edit_shift(db, id, shift_name, shift_desc, shift_start_date, shift_end_date,
                                        action_user)
        if db_shift is None:
            status = 418
            error_msg = 'edit_shift_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_shift = None
        error_msg = 'edit_shift_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift}


def change_shift_state(db: Session, id, state, action_user):
    try:
        db_shift = get_shift_by_id(db, id)
        status = db_shift["status"]
        error_msg = db_shift["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_shift["result"]}
        db_shift = temp_crud.change_shift_state(db, id, state, action_user)
        if db_shift is None:
            status = 418
            error_msg = 'change_shift_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_shift = None
        error_msg = 'change_shift_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift}


def get_shift_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_shift = temp_crud.get_shift_by_id(db, id)
        if db_shift is None:
            status = 418
            error_msg = 'get_shift_detail_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_shift = None
        error_msg = 'get_shift_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift}


def get_shift_by_datetime(db: Session, order_date):
    try:
        status = 200
        error_msg = ''
        shift_id = None
        now = datetime.now()
        db_shift = temp_crud.get_shift_list(db)
        if db_shift:
            order_date = str(order_date).split('.', 1)[0]
            order_date = datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            order_date = datetime.strptime(str(now.date()) + ' ' + str(order_date.time()),
                                           '%Y-%m-%d %H:%M:%S')
            for shift in db_shift:
                if shift.shift_start_time < shift.shift_end_time:
                    shift_date_start = datetime.now()
                    shift_date_end = datetime.now()
                    shift_date_start_1 = datetime.now() - timedelta(days=1)
                    shift_date_end_1 = datetime.now() - timedelta(days=1)
                else:
                    shift_date_start = datetime.now()
                    shift_date_end = datetime.now() + timedelta(days=1)
                    shift_date_start_1 = datetime.now() - timedelta(days=1)
                    shift_date_end_1 = datetime.now()
                start_date = datetime.strptime(str(shift_date_start.date()) + ' ' + str(shift.shift_start_time.time()),
                                               '%Y-%m-%d %H:%M:%S')
                end_date = datetime.strptime(str(shift_date_end.date()) + ' ' + str(shift.shift_end_time.time()),
                                             '%Y-%m-%d %H:%M:%S')
                start_date_1 = datetime.strptime(
                    str(shift_date_start_1.date()) + ' ' + str(shift.shift_start_time.time()),
                    '%Y-%m-%d %H:%M:%S')
                end_date_1 = datetime.strptime(str(shift_date_end_1.date()) + ' ' + str(shift.shift_end_time.time()),
                                               '%Y-%m-%d %H:%M:%S')
                if start_date <= order_date <= end_date:
                    shift_id = shift.id
                elif start_date_1 <= order_date <= end_date_1:
                    shift_id = shift.id
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        shift_id = None
        error_msg = 'get_shift_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": shift_id}


def get_shift_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_shift = temp_crud.get_shift_list(db)
        if db_shift is None:
            status = 418
            error_msg = 'get_shift_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_shift = None
        error_msg = 'get_shift_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift}


def get_shift_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_shift = temp_crud.get_shift_active_list(db)
        if db_shift is None:
            status = 418
            error_msg = 'get_shift_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_shift = None
        error_msg = 'get_shift_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift}


def get_active_shift_search(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_shift = temp_crud.get_active_shift_search(db, search_text)
        if db_shift is None:
            status = 418
            error_msg = 'get_shift_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_shift = None
        error_msg = 'get_shift_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift}


# endregion


# region Shift Vehicles
def add_shift_vehicle(db: Session, shift_id, vehicle_id, action_user):
    try:
        status = 200
        error_msg = ''
        db_vehicle = temp_crud.get_shift_vehicle_by_info(db, shift_id, vehicle_id)
        if db_vehicle is None:
            db_shift_vehicle = temp_crud.add_shift_vehicle(db, shift_id, vehicle_id, action_user)
            if db_shift_vehicle is None:
                status = 418
                error_msg = 'add_shift_vehicle_failed'
        else:
            if db_vehicle.state == models.EntityState.active:
                status = 418
                db_shift_vehicle = None
                error_msg = 'warehouse_user_conflict'
            else:
                db_shift_vehicle = change_shift_vehicle_state(db, db_vehicle.id, models.EntityState.active,
                                                              action_user)
                status = db_shift_vehicle["status"]
                error_msg = db_shift_vehicle["error_msg"]
                db_shift_vehicle = db_shift_vehicle["result"]
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_shift_vehicle = None
        error_msg = 'add_shift_vehicle_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift_vehicle}


def change_shift_vehicle_state(db: Session, id, state, action_user):
    try:
        db_shift_vehicle = get_shift_vehicle_by_id(db, id)
        status = db_shift_vehicle["status"]
        error_msg = db_shift_vehicle["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_shift_vehicle["result"]}
        db_shift_vehicle = temp_crud.change_shift_vehicle_state(db, id, state, action_user)
        if db_shift_vehicle is None:
            status = 418
            error_msg = 'change_shift_vehicle_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_shift_vehicle = None
        error_msg = 'change_shift_vehicle_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift_vehicle}


def get_shift_vehicle_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_shift_vehicle = temp_crud.get_shift_vehicle_by_id(db, id)
        if db_shift_vehicle is None:
            status = 418
            error_msg = 'get_shift_vehicle_detail_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_shift_vehicle = None
        error_msg = 'get_shift_vehicle_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift_vehicle}


def get_shift_vehicle_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_shift_vehicle = temp_crud.get_shift_vehicle_list(db)
        if db_shift_vehicle is None:
            status = 418
            error_msg = 'get_shift_vehicle_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_shift_vehicle = None
        error_msg = 'get_shift_vehicle_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift_vehicle}


def get_shift_vehicle_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_shift_vehicle = temp_crud.get_shift_vehicle_active_list(db)
        if db_shift_vehicle is None:
            status = 418
            error_msg = 'get_shift_vehicle_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_shift_vehicle = None
        error_msg = 'get_shift_vehicle_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift_vehicle}


def get_active_shift_vehicle_search(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_shift_vehicle = temp_crud.get_active_shift_vehicle_search(db, search_text)
        if db_shift_vehicle is None:
            status = 418
            error_msg = 'get_shift_vehicle_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_shift_vehicle = None
        error_msg = 'get_shift_vehicle_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift_vehicle}


def get_active_shift_vehicle_search_by_shift(db: Session, search_text, shift_id):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_shift_vehicle = temp_crud.get_active_shift_vehicle_search_by_shift(db, search_text, shift_id)
        if db_shift_vehicle is None:
            status = 418
            error_msg = 'get_active_shift_vehicle_search_by_shift_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_shift_vehicle = None
        error_msg = 'get_active_shift_vehicle_search_by_shift_error'
    return {"status": status, "error_msg": error_msg, "result": db_shift_vehicle}


# endregion


# region Services
def add_service(db: Session, service_name, service_desc, service_priority, action_user):
    try:
        status = 200
        error_msg = ''
        db_service = temp_crud.add_service(db, service_name, service_desc, service_priority, action_user)
        if db_service is None:
            status = 418
            error_msg = 'add_service_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_service = None
        error_msg = 'add_service_error'
    return {"status": status, "error_msg": error_msg, "result": db_service}


def edit_service(db: Session, id, service_name, service_desc, service_priority, action_user):
    try:
        db_service = get_service_by_id(db, id)
        status = db_service["status"]
        error_msg = db_service["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_service["result"]}
        db_service = temp_crud.edit_service(db, id, service_name, service_desc, service_priority, action_user)
        if db_service is None:
            status = 418
            error_msg = 'edit_service_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_service = None
        error_msg = 'edit_service_error'
    return {"status": status, "error_msg": error_msg, "result": db_service}


def change_service_state(db: Session, id, state, action_user):
    try:
        db_service = get_service_by_id(db, id)
        status = db_service["status"]
        error_msg = db_service["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_service["result"]}
        db_service = temp_crud.change_service_state(db, id, state, action_user)
        if db_service is None:
            status = 418
            error_msg = 'change_service_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_service = None
        error_msg = 'change_service_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_service}


def get_service_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_service = temp_crud.get_service_by_id(db, id)
        if db_service is None:
            status = 418
            error_msg = 'get_service_detail_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_service = None
        error_msg = 'get_service_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_service}


def get_service_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_service = temp_crud.get_service_list(db)
        if db_service is None:
            status = 418
            error_msg = 'get_service_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_service = None
        error_msg = 'get_service_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_service}


def get_service_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_service = temp_crud.get_service_active_list(db)
        if db_service is None:
            status = 418
            error_msg = 'get_service_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_service = None
        error_msg = 'get_service_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_service}


def get_active_service_search(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_service = temp_crud.get_active_service_search(db, search_text)
        if db_service is None:
            status = 418
            error_msg = 'get_service_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_service = None
        error_msg = 'get_service_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_service}


# endregion


# region Service Vehicles
def add_service_vehicle(db: Session, service_id, vehicle_id, action_user):
    try:
        status = 200
        error_msg = ''
        db_vehicle = temp_crud.get_service_vehicle_by_info(db, service_id, vehicle_id)
        if db_vehicle is None:
            db_service_vehicle = temp_crud.add_service_vehicle(db, service_id, vehicle_id, action_user)
            if db_service_vehicle is None:
                status = 418
                error_msg = 'add_service_vehicle_failed'
        else:
            if db_vehicle.state == models.EntityState.active:
                status = 418
                db_service_vehicle = None
                error_msg = 'warehouse_user_conflict'
            else:
                db_service_vehicle = change_service_vehicle_state(db, db_vehicle.id, models.EntityState.active,
                                                                  action_user)
                status = db_service_vehicle["status"]
                error_msg = db_service_vehicle["error_msg"]
                db_service_vehicle = db_service_vehicle["result"]
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_service_vehicle = None
        error_msg = 'add_service_vehicle_error'
    return {"status": status, "error_msg": error_msg, "result": db_service_vehicle}


def change_service_vehicle_state(db: Session, id, state, action_user):
    try:
        db_service_vehicle = get_service_vehicle_by_id(db, id)
        status = db_service_vehicle["status"]
        error_msg = db_service_vehicle["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_service_vehicle["result"]}
        db_service_vehicle = temp_crud.change_service_vehicle_state(db, id, state, action_user)
        if db_service_vehicle is None:
            status = 418
            error_msg = 'change_service_vehicle_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_service_vehicle = None
        error_msg = 'change_service_vehicle_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_service_vehicle}


def get_service_vehicle_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_service_vehicle = temp_crud.get_service_vehicle_by_id(db, id)
        if db_service_vehicle is None:
            status = 418
            error_msg = 'get_service_vehicle_detail_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_service_vehicle = None
        error_msg = 'get_service_vehicle_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_service_vehicle}


def get_service_vehicle_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_service_vehicle = temp_crud.get_service_vehicle_list(db)
        if db_service_vehicle is None:
            status = 418
            error_msg = 'get_service_vehicle_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_service_vehicle = None
        error_msg = 'get_service_vehicle_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_service_vehicle}


def get_service_vehicle_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_service_vehicle = temp_crud.get_service_vehicle_active_list(db)
        if db_service_vehicle is None:
            status = 418
            error_msg = 'get_service_vehicle_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_service_vehicle = None
        error_msg = 'get_service_vehicle_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_service_vehicle}


def get_active_service_vehicle_search(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_service_vehicle = temp_crud.get_active_service_vehicle_search(db, search_text)
        if db_service_vehicle is None:
            status = 418
            error_msg = 'get_service_vehicle_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_service_vehicle = None
        error_msg = 'get_service_vehicle_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_service_vehicle}


def get_active_service_vehicle_search_by_service(db: Session, search_text, service_id):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_service_vehicle = temp_crud.get_active_service_vehicle_search_by_service(db, search_text, service_id)
        if db_service_vehicle is None:
            status = 418
            error_msg = 'get_active_service_vehicle_search_by_service_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_service_vehicle = None
        error_msg = 'get_active_service_vehicle_search_by_service_error'
    return {"status": status, "error_msg": error_msg, "result": db_service_vehicle}


# endregion


# region Districts
def add_district(db: Session, district_name, district_desc, district_geo, action_user):
    try:
        status = 200
        error_msg = ''
        district_map = json.loads(district_geo)
        district_geo = district_map["geometry"]["coordinates"][0]
        district_geo = Polygon(district_geo)
        district_geo = wkb.dumps(district_geo, hex=True)
        db_district = temp_crud.add_district(db, district_name, district_desc, district_geo, action_user)
        if db_district is None:
            status = 418
            error_msg = 'add_district_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_district = None
        error_msg = 'add_district_error'
    return {"status": status, "error_msg": error_msg, "result": db_district}


def edit_district(db: Session, id, district_name, district_desc, district_geo, action_user):
    try:
        status = 200
        error_msg = ''
        db_district = temp_crud.get_district_by_id(db, id)
        if db_district is None:
            status = 418
            error_msg = 'get_district_detail_by_id_failed'
        district_geo = json.loads(district_geo)
        district_geo = Polygon(district_geo)
        district_geo = wkb.dumps(district_geo, hex=True)
        db_district = temp_crud.edit_district(db, id, district_name, district_desc, district_geo, action_user)
        if db_district is None:
            status = 418
            error_msg = 'edit_district_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_district = None
        error_msg = 'edit_district_error'
    return {"status": status, "error_msg": error_msg, "result": db_district}


def change_district_state(db: Session, id, state, action_user):
    try:
        status = 200
        error_msg = ''
        db_district = temp_crud.get_district_by_id(db, id)
        if db_district is None:
            status = 418
            error_msg = 'get_district_detail_by_id_failed'
        db_district = temp_crud.change_district_state(db, id, state, action_user)
        if db_district is None:
            status = 418
            error_msg = 'change_district_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_district = None
        error_msg = 'change_district_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_district}


def get_district_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_district = temp_crud.get_district_by_id(db, id)
        if db_district is None:
            status = 418
            error_msg = 'get_district_detail_by_id_failed'
        if db_district.district_geo:
            db_district.district_geo = wkb.loads(db_district.district_geo, hex=True)
            db_district.district_geo = list(db_district.district_geo.exterior.coords)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_district = None
        error_msg = 'get_district_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_district}


def get_district_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_district = temp_crud.get_district_list(db)
        if db_district is None:
            status = 418
            error_msg = 'get_district_list_failed'
        for item in db_district:
            item.district_geo = wkb.loads(item.district_geo, hex=True)
            item.district_geo = list(item.district_geo.exterior.coords)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_district = None
        error_msg = 'get_district_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_district}


def get_district_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        result = []
        db_district = temp_crud.get_district_active_list(db)
        if db_district is None:
            status = 418
            error_msg = 'get_district_active_list_failed'
        for item in db_district:
            district_geo = wkb.loads(item.district_geo)
            district_geo = list(district_geo.exterior.coords)
            result.append({"id": item.id,
                           "district_name": item.district_name,
                           "district_desc": item.district_desc,
                           "district_geo": district_geo,
                           "state": item.state,
                           "create_ts": item.create_ts,
                           "update_ts": item.update_ts})
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        result = None
        error_msg = 'get_district_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": result}


def get_district_active_list_no_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_district = temp_crud.get_district_active_list_no_id(db, id)
        if db_district is None:
            status = 418
            error_msg = 'get_district_active_list_no_id_failed'
        for item in db_district:
            if item.district_geo:
                item.district_geo = wkb.loads(item.district_geo, hex=True)
                item.district_geo = list(item.district_geo.exterior.coords)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_district = None
        error_msg = 'get_district_active_list_no_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_district}


def get_district_active_list_with_drivers(db: Session):
    try:
        status = 200
        error_msg = ''
        db_district = temp_crud.get_district_active_list_with_drivers(db)
        if db_district is None:
            status = 418
            error_msg = 'get_district_active_list_with_drivers_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_district = None
        error_msg = 'get_district_active_list_with_drivers_error'
    return {"status": status, "error_msg": error_msg, "result": db_district}


def get_active_district_search(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_district = temp_crud.get_active_district_search(db, search_text)
        if db_district is None:
            status = 418
            error_msg = 'get_district_active_list_failed'
        for item in db_district:
            if item.district_geo:
                item.district_geo = wkb.loads(item.district_geo, hex=True)
                item.district_geo = list(item.district_geo.exterior.coords)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_district = None
        error_msg = 'get_district_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_district}


def get_district_driver(db: Session, driver_id, district_id):
    try:
        status = 200
        error_msg = ''
        district_order = 0
        db_district = temp_crud.get_district_driver(db, district_id)
        if db_district is None:
            status = 418
            error_msg = 'get_district_driver_failed'
        else:
            for district in db_district:
                district_order += 1
                if district.driver_id == driver_id:
                    break
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        district_order = 0
        error_msg = 'get_district_driver_error'
    return {"status": status, "error_msg": error_msg, "result": district_order}


# endregion


# region Rates
def add_rate(db: Session, rate_name, rate_desc, service_id, shift_id, district_ids, start_date, end_date, price_km,
             price_min, price_wait_min, minute_free_wait, price_delivery, minute_for_wait, km_free, price_cancel,
             price_minimal, service_prc, birthday_discount_prc, action_user):
    try:
        status = 200
        error_msg = ''
        district_names = []
        if district_ids:
            district_ids = district_ids.split(',')
            for id in district_ids:
                db_district = temp_crud.get_district_by_id(db, id)
                district_names.append({"tm": db_district.district_name["tm"],
                                       "ru": db_district.district_name["ru"],
                                       "en": db_district.district_name["en"]})
        else:
            district_ids = []
            district_names.append({"tm": "", "ru": "", "en": ""})

        db_rate = temp_crud.add_rate(db, rate_name, rate_desc, service_id, shift_id, district_ids, district_names,
                                     start_date, end_date, price_km, price_min, price_wait_min, minute_free_wait,
                                     price_delivery, minute_for_wait, km_free, price_cancel, price_minimal, service_prc,
                                     birthday_discount_prc, action_user)
        if db_rate is None:
            status = 418
            error_msg = 'add_rate_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_rate = None
        error_msg = 'add_rate_error'
    return {"status": status, "error_msg": error_msg, "result": db_rate}


def edit_rate(db: Session, id, rate_name, rate_desc, service_id, shift_id, district_ids, start_date, end_date, price_km,
              price_min, minute_free_wait, price_delivery, minute_for_wait, price_cancel, price_minimal, service_prc,
              birthday_discount_prc, action_user):
    try:
        status = 200
        error_msg = ''
        district_names = []
        if district_ids:
            district_ids = district_ids.split(',')
            for district_id in district_ids:
                db_district = temp_crud.get_district_by_id(db, district_id)
                district_names.append({"tm": db_district.district_name["tm"],
                                       "ru": db_district.district_name["ru"],
                                       "en": db_district.district_name["en"]})
        else:
            district_ids = []
            district_names.append({"tm": "", "ru": "", "en": ""})
        db_rate = temp_crud.edit_rate(db, id, rate_name, rate_desc, service_id, shift_id, district_ids, district_names,
                                      start_date, end_date, price_km, price_min, minute_free_wait, price_delivery,
                                      minute_for_wait, price_cancel, price_minimal, service_prc, birthday_discount_prc,
                                      action_user)
        if db_rate is None:
            status = 418
            error_msg = 'edit_rate_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_rate = None
        error_msg = 'edit_rate_error'
    return {"status": status, "error_msg": error_msg, "result": db_rate}


def change_rate_state(db: Session, id, state, action_user):
    try:
        db_rate = get_rate_by_id(db, id)
        status = db_rate["status"]
        error_msg = db_rate["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": db_rate["result"]}
        db_rate = temp_crud.change_rate_state(db, id, state, action_user)
        if db_rate is None:
            status = 418
            error_msg = 'change_rate_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_rate = None
        error_msg = 'change_rate_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_rate}


def get_rate_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_rate = temp_crud.get_rate_by_id(db, id)
        if db_rate is None:
            status = 418
            error_msg = 'get_rate_detail_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_rate = None
        error_msg = 'get_rate_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_rate}


def get_rate_by_info(db: Session, service_id, district_id, order_date):
    status = 200
    error_msg = ''
    if district_id == 'null':
        district_id = None
    db_shift = get_shift_by_datetime(db, order_date)
    shift_id = db_shift["result"]
    db_rate = temp_crud.get_rate_by_info(db, service_id, shift_id, district_id, order_date)
    return {"status": status, "error_msg": error_msg, "result": db_rate}


def get_rate_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_rate = temp_crud.get_rate_list(db)
        if db_rate is None:
            status = 418
            error_msg = 'get_rate_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_rate = None
        error_msg = 'get_rate_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_rate}


def get_rate_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_rate = temp_crud.get_rate_active_list(db)
        if db_rate is None:
            status = 418
            error_msg = 'get_rate_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_rate = None
        error_msg = 'get_rate_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_rate}


def get_active_rate_list_by_info(db: Session, district_id, order_date):
    try:
        status = 200
        error_msg = ''
        if district_id == 'null':
            district_id = None
        db_shift = get_shift_by_datetime(db, order_date)
        shift_id = db_shift["result"]
        db_service = temp_crud.get_service_active_list(db)
        result = []
        for service in db_service:
            db_rate = temp_crud.get_rate_by_info_service(db, service.id, shift_id, district_id, order_date)
            if db_rate:
                result.append({"rate_id": db_rate.id,
                               "service_id": db_rate.service_id,
                               "shift_id": db_rate.shift_id,
                               "start_date": db_rate.start_date,
                               "end_date": db_rate.end_date,
                               "price_km": db_rate.price_km,
                               "price_min": db_rate.price_min,
                               "minute_free_wait": db_rate.minute_free_wait,
                               "price_delivery": db_rate.price_delivery,
                               "minute_for_wait": db_rate.minute_for_wait,
                               "price_cancel": db_rate.price_cancel,
                               "price_minimal": db_rate.price_minimal,
                               "service_prc": db_rate.service_prc,
                               "birthday_discount_prc": db_rate.birthday_discount_prc,
                               "service_name": db_rate.service_name,
                               "shift_name": db_rate.shift_name})
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        result = None
        error_msg = 'get_rate_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": result}


def get_active_rate_list_by_geo_info(db: Session, district_id, order_date, latitude_from, longitude_from, latitude_to,
                                     longitude_to):
    try:
        status = 200
        error_msg = ''
        address1 = (latitude_from, longitude_from)
        address2 = (latitude_to, longitude_to)
        distance = geodesic(address1, address2).kilometers
        time = math.ceil(distance)
        if district_id == 'null':
            district_id = None
        db_shift = get_shift_by_datetime(db, order_date)
        shift_id = db_shift["result"]
        db_service = temp_crud.get_service_active_list(db)
        result = []
        for service in db_service:
            db_rate = temp_crud.get_rate_by_info_service(db, service.id, shift_id, district_id, order_date)
            if db_rate:
                order_distance = distance - db_rate.km_free
                order_distance2 = order_distance
                if order_distance <= 0:
                    order_distance = 0
                order_price = float(db_rate.price_delivery) + (float(db_rate.price_km) * order_distance) + (
                            float(db_rate.price_min) * time)
                if order_price < db_rate.price_minimal:
                    order_price = db_rate.price_minimal
                result.append({"rate_id": db_rate.id,
                               "service_id": db_rate.service_id,
                               "shift_id": db_rate.shift_id,
                               "start_date": db_rate.start_date,
                               "end_date": db_rate.end_date,
                               "price_km": db_rate.price_km,
                               "price_min": db_rate.price_min,
                               "price_wait_min": db_rate.price_wait_min,
                               "minute_free_wait": db_rate.minute_free_wait,
                               "km_free": db_rate.km_free,
                               "price_delivery": db_rate.price_delivery,
                               "minute_for_wait": db_rate.minute_for_wait,
                               "price_cancel": db_rate.price_cancel,
                               "price_minimal": db_rate.price_minimal,
                               "service_prc": db_rate.service_prc,
                               "birthday_discount_prc": db_rate.birthday_discount_prc,
                               "service_name": db_rate.service_name,
                               "shift_name": db_rate.shift_name,
                               "order_distance": math.ceil(order_distance2),
                               "order_price": math.ceil(order_price),
                               "order_time": math.ceil(time)})
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        result = None
        error_msg = 'get_rate_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": result}


def get_rate_active_list_view(db: Session):
    try:
        status = 200
        error_msg = ''
        db_rate = temp_crud.get_rate_active_list_view(db)
        if db_rate is None:
            status = 418
            error_msg = 'get_rate_active_list_view_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_rate = None
        error_msg = 'get_rate_active_list_view_error'
    return {"status": status, "error_msg": error_msg, "result": db_rate}


def get_active_rate_search(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_rate = temp_crud.get_active_rate_search(db, search_text)
        if db_rate is None:
            status = 418
            error_msg = 'search_rate_active_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_rate = None
        error_msg = 'search_rate_active_error'
    return {"status": status, "error_msg": error_msg, "result": db_rate}

# endregion
