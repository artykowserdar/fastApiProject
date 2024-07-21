import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import FlushError

from app import config, models
from app.accesses import temp_access
from app.cruds import customer_crud

log = logging.getLogger(__name__)

static_path = config.IMAGE_FULL_URL + '/customers'


# region Customer
def add_customer(db: Session, username, fullname, initials, address, birth_date, birth_place, gender, customer_type,
                 employee_type, discount_percent, discount_limit, card_no, phone, image, action_user):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_by_phone(db, phone)
        if db_customer:
            if db_customer.state == models.EntityState.deleted:
                customer_crud.change_customer_state(db, db_customer.id, models.EntityState.active, action_user)
            else:
                status = 418
                error_msg = 'Клиент уже присутствует с этим телефоном'
                return {"status": status, "error_msg": error_msg, "result": None}
        else:
            code = temp_access.create_employee_code(employee_type)
            db_image = temp_access.create_image(image, 'no-image', static_path)
            status = db_image["status"]
            error_msg = db_image["error_msg"]
            if status == 418:
                return {"status": status, "error_msg": error_msg, "result": db_image["result"]}
            create_image = db_image["result"]
            image_name = create_image["imagename"]
            image_path = create_image["destination_image"]
            db_customer = customer_crud.add_customer(db, fullname, initials, address, birth_date, birth_place, gender,
                                                     customer_type, code, discount_percent, discount_limit, card_no,
                                                     phone, username, employee_type, image_name, image_path,
                                                     action_user)
            if db_customer is None:
                status = 418
                error_msg = 'add_customer_failed'
                return {"status": status, "error_msg": error_msg, "result": None}
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_customer = None
        error_msg = 'add_customer_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def edit_customer(db: Session, id, fullname, initials, address, birth_date, birth_place, gender, customer_type,
                  employee_type, discount_percent, discount_limit, card_no, phone, image, action_user):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_by_phone_no_id(db, id, phone)
        if db_customer:
            status = 418
            error_msg = 'Клиент уже присутствует с этим телефоном'
            return {"status": status, "error_msg": error_msg, "result": None}
        else:
            if image is None:
                customer = customer_crud.get_customer_by_id_sample(db, id)
                image_name = customer.image_name
                image_path = customer.image_path
            else:
                db_image = temp_access.create_image(image, 'no-image', static_path)
                status = db_image["status"]
                error_msg = db_image["error_msg"]
                if status == 418:
                    return {"status": status, "error_msg": error_msg, "result": db_image["result"]}
                create_image = db_image["result"]
                image_name = create_image["imagename"]
                image_path = create_image["destination_image"]
            db_customer = customer_crud.edit_customer(db, id, fullname, initials, address, birth_date, birth_place,
                                                      gender, customer_type, discount_percent, discount_limit, card_no,
                                                      phone, employee_type, image_name, image_path, action_user)
            if db_customer is None:
                status = 418
                error_msg = 'edit_customer_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_customer = None
        error_msg = 'edit_customer_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def add_customer_blacklist(db: Session, id, blacklist, action_user):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.add_customer_blacklist(db, id, blacklist, action_user)
        if db_customer is None:
            status = 418
            error_msg = 'add_customer_to_blacklist_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_customer = None
        error_msg = 'add_customer_to_blacklist_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def add_user_to_customer(db: Session, username, id, action_user):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.add_user_to_customer(db, id, username, action_user)
        if db_customer is None:
            status = 418
            error_msg = 'add_user_to_customer_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_customer = None
        error_msg = 'add_user_to_customer_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def change_customer_state(db: Session, id, state, action_user):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.change_customer_state(db, id, state, action_user)
        if db_customer is None:
            status = 418
            error_msg = 'change_customer_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_customer = None
        error_msg = 'change_customer_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_by_id(db, id)
        if db_customer is None:
            status = 418
            error_msg = 'get_customer_detail_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'get_customer_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_by_phone(db: Session, phone):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_by_phone(db, phone)
        if db_customer is None:
            status = 418
            error_msg = 'Клиент не найден'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'get_customer_by_phone_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_by_username(db: Session, username):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_by_username(db, username)
        if db_customer is None:
            status = 418
            error_msg = 'get_customer_by_username_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'get_customer_by_username_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_list_simple(db: Session):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_list_simple(db)
        if db_customer is None:
            status = 418
            error_msg = 'get_customer_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'get_customer_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_active_list(db)
        if db_customer is None:
            status = 418
            error_msg = 'get_customer_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'get_customer_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_active_list_by_type(db: Session, customer_type):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_active_list_by_type(db, customer_type)
        if db_customer is None:
            status = 418
            error_msg = 'get_customer_active_list_by_customer_type_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'get_customer_active_list_by_customer_type_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_active_list_employee(db: Session):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_active_list_employee(db)
        if db_customer is None:
            status = 418
            error_msg = 'get_customer_active_list_employee_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'get_customer_active_list_employee_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_active_list_employee_driver(db: Session):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_active_list_employee_driver(db)
        if db_customer is None:
            status = 418
            error_msg = 'get_customer_active_list_employee_driver_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'get_customer_active_list_employee_driver_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_active_list_by_type_not_blacklist(db: Session, customer_type):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_active_list_by_type_not_blacklist(db, customer_type)
        if db_customer is None:
            status = 418
            error_msg = 'get_not_in_blacklist_customer_active_list_by_customer_type_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'get_not_in_blacklist_customer_active_list_by_customer_type_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_active_list_not_assigned(db: Session):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_active_list_not_assigned(db)
        if db_customer is None:
            status = 418
            error_msg = 'get_customer_active_list_not_assigned_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'get_customer_active_list_not_assigned_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_active_list_not_assigned_user(db: Session, username):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_active_list_not_assigned_user(db, username)
        if db_customer is None:
            status = 418
            error_msg = 'get_customer_active_list_not_assigned_user_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'get_customer_active_list_not_assigned_user_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_active_list_by_employee_type(db: Session, employee_type):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_active_list_by_employee_type(db, employee_type)
        if db_customer is None:
            status = 418
            error_msg = 'get_customer_active_list_by_employee_type_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'get_customer_active_list_by_employee_type_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def search(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_customer = customer_crud.search(db, search_text)
        if db_customer is None:
            status = 418
            error_msg = 'search_customer_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'search_customer_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def search_active(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_customer = customer_crud.search_active(db, search_text)
        if db_customer is None:
            status = 418
            error_msg = 'search_active_customer_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'search_active_customer_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def search_active_by_type(db: Session, search_text, customer_type):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_customer = customer_crud.search_active_by_type(db, search_text, customer_type)
        if db_customer is None:
            status = 418
            error_msg = 'search_active_customer_by_customer_type_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'search_active_customer_by_customer_type_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def search_active_by_employee_type(db: Session, search_text, employee_type):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_customer = customer_crud.search_active_by_employee_type(db, search_text, employee_type)
        if db_customer is None:
            status = 418
            error_msg = 'search_active_by_employee_type_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'search_active_by_employee_type_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


# endregion


# region Customer Balances
def add_balance_to_customer(db: Session, customer_id, service_amount: float, in_out, service_amount_old: float,
                            action_user):
    try:
        status = 200
        error_msg = ''
        db_customer_balance = customer_crud.get_customer_balance_by_customer(db, customer_id)
        if db_customer_balance:
            if in_out:
                current_balance = db_customer_balance.current_balance - service_amount_old + service_amount
            else:
                current_balance = db_customer_balance.current_balance + service_amount_old - service_amount
            db_customer_balance = customer_crud.edit_customer_balance(db, db_customer_balance.id,
                                                                      round(current_balance, 2), action_user)
            if db_customer_balance is None:
                status = 418
                error_msg = 'add_balance_to_customer_failed'
        else:
            if in_out:
                current_balance = service_amount_old + service_amount
            else:
                current_balance = service_amount_old - service_amount
            db_customer_balance = customer_crud.add_customer_balance(db, customer_id, round(current_balance, 2),
                                                                     action_user)
            if db_customer_balance is None:
                status = 418
                error_msg = 'add_balance_to_customer_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_customer_balance = None
        error_msg = 'add_balance_to_customer_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer_balance}


def get_customer_balance_by_customer(db: Session, customer_id):
    try:
        status = 200
        error_msg = ''
        db_customer_balance = customer_crud.get_customer_balance_by_customer(db, customer_id)
        if db_customer_balance is None:
            status = 418
            error_msg = 'get_customer_balance_detail_by_customer_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer_balance = None
        error_msg = 'get_customer_balance_detail_by_customer_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer_balance}


def get_all_customer_balance_sum(db: Session):
    try:
        status = 200
        error_msg = ''
        db_customer_balance = customer_crud.get_all_customer_balance_sum(db)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer_balance = None
        error_msg = 'get_all_customer_balance_sum_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer_balance}


# endregion


# region Client Address History
def add_client_address_history(db: Session, client_id, district_id, address_type, address, coordinates, action_user):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_client_address_history_by_coordinates(db, client_id, address_type, coordinates)
        if db_customer is None:
            db_customer = customer_crud.add_client_address_history(db, client_id, district_id, address_type, address,
                                                                   coordinates)
            if db_customer is None:
                status = 418
                error_msg = 'add_client_address_history_failed'
        else:
            if db_customer.state == models.EntityState.deleted:
                db_customer = customer_crud.change_client_address_history_state(db, db_customer.id,
                                                                                models.EntityState.active)
                if db_customer is None:
                    status = 418
                    error_msg = 'change_client_address_history_state_failed'
            else:
                customer_crud.update_client_address_history(db, db_customer.id)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_customer = None
        error_msg = 'add_client_address_history_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def change_client_address_history_state(db: Session, id, state, action_user):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.change_client_address_history_state(db, id, state)
        if db_customer is None:
            status = 418
            error_msg = 'change_client_address_history_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_customer = None
        error_msg = 'change_client_address_history_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_client_address_history_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_client_address_history = customer_crud.get_client_address_history_list(db)
        if db_client_address_history is None:
            status = 418
            error_msg = 'get_client_address_history_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_client_address_history = None
        error_msg = 'get_client_address_history_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_client_address_history}


def get_client_address_history_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_client_address_history = customer_crud.get_client_address_history_active_list(db)
        if db_client_address_history is None:
            status = 418
            error_msg = 'get_client_address_history_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_client_address_history = None
        error_msg = 'get_client_address_history_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_client_address_history}


def get_client_address_history_active_list_by_client(db: Session, client_id):
    try:
        status = 200
        error_msg = ''
        db_client_address_history = customer_crud \
            .get_client_address_history_active_list_by_client(db, client_id)
        if db_client_address_history is None:
            status = 418
            error_msg = 'get_client_address_history_active_list_by_client_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_client_address_history = None
        error_msg = 'get_client_address_history_active_list_by_client_error'
    return {"status": status, "error_msg": error_msg, "result": db_client_address_history}


def get_client_address_history_active_list_by_client_type(db: Session, client_id, address_type):
    try:
        status = 200
        error_msg = ''
        db_client_address_history = customer_crud \
            .get_client_address_history_active_list_by_client_type(db, client_id, address_type)
        if db_client_address_history is None:
            status = 418
            error_msg = 'get_client_address_history_active_list_by_client_type_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_client_address_history = None
        error_msg = 'get_client_address_history_active_list_by_client_type_error'
    return {"status": status, "error_msg": error_msg, "result": db_client_address_history}


def get_client_address_history_active_list_by_type_order(db: Session, client_id, address_type):
    try:
        status = 200
        error_msg = ''
        response = []
        db_client_address_history = customer_crud \
            .get_client_address_history_active_list_by_type_order(db, client_id, address_type)
        if db_client_address_history is None:
            status = 418
            error_msg = 'get_client_address_history_active_list_by_type_order_failed'
        else:
            for location in db_client_address_history:
                coordinates = location.coordinates.split(",")
                response.append({"latitude": coordinates[0],
                                 "longitude": coordinates[1],
                                 "address": location.address,
                                 "district_id": location.district_id})
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        response = None
        error_msg = 'get_client_address_history_active_list_by_type_order_error'
    return {"status": status, "error_msg": error_msg, "result": response}


def search_active_client_address_history_by_client_type(db: Session, search_text, client_id, address_type):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_customer = customer_crud \
            .search_active_client_address_history_by_client_type(db, search_text, client_id, address_type)
        if db_customer is None:
            status = 418
            error_msg = 'search_active_client_address_history_by_client_type_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer = None
        error_msg = 'search_active_client_address_history_by_client_type_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


# endregion


# region Customer Ratings
def add_customer_rating(db: Session, set_customer_id, get_customer_id, rating, comment, action_user):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.get_customer_rating_by_info(db, set_customer_id, get_customer_id)
        if db_customer is None:
            db_customer = customer_crud.add_customer_rating(db, set_customer_id, get_customer_id, rating, comment)
            if db_customer is None:
                status = 418
                error_msg = 'add_customer_rating_failed'
        else:
            if db_customer.state == models.EntityState.deleted:
                db_customer = customer_crud.update_customer_rating_state(db, db_customer.id, rating, comment,
                                                                         models.EntityState.active)
                if db_customer is None:
                    status = 418
                    error_msg = 'change_customer_rating_state_failed'
            else:
                db_customer = customer_crud.edit_customer_rating(db, db_customer.id, rating, comment)
                if db_customer is None:
                    status = 418
                    error_msg = 'edit_customer_rating_failed'
        db.commit()
        db_rating = customer_crud.get_customer_rating_active_group_by_get_customer(db, get_customer_id)
        customer_crud.edit_customer_rating_data(db, get_customer_id, db_rating.rating)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_customer = None
        error_msg = 'add_customer_rating_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def edit_customer_rating(db: Session, id, rating, comment, action_user):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.edit_customer_rating(db, id, rating, comment)
        if db_customer is None:
            status = 418
            error_msg = 'edit_customer_rating_failed'
        db.commit()
        rating = 0
        db_customer = customer_crud.get_customer_rating_by_id(db, id)
        db_rating = customer_crud.get_customer_rating_active_group_by_get_customer(db, db_customer.get_customer_id)
        if db_rating:
            rating = db_rating.rating
        customer_crud.edit_customer_rating_data(db, db_customer.get_customer_id, rating)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_customer = None
        error_msg = 'edit_customer_rating_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def update_customer_rating_state(db: Session, id, rating, comment, state, action_user):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.update_customer_rating_state(db, id, rating, comment, state)
        if db_customer is None:
            status = 418
            error_msg = 'update_customer_rating_state_failed'
        db.commit()
        rating = 0
        db_customer = customer_crud.get_customer_rating_by_id(db, id)
        db_rating = customer_crud.get_customer_rating_active_group_by_get_customer(db, db_customer.get_customer_id)
        if db_rating:
            rating = db_rating.rating
        customer_crud.edit_customer_rating_data(db, db_customer.get_customer_id, rating)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_customer = None
        error_msg = 'update_customer_rating_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def change_customer_rating_state(db: Session, id, state, action_user):
    try:
        status = 200
        error_msg = ''
        db_customer = customer_crud.change_customer_rating_state(db, id, state)
        if db_customer is None:
            status = 418
            error_msg = 'change_customer_rating_state_failed'
        db.commit()
        rating = 0
        db_customer = customer_crud.get_customer_rating_by_id(db, id)
        db_rating = customer_crud.get_customer_rating_active_group_by_get_customer(db, db_customer.get_customer_id)
        if db_rating:
            rating = db_rating.rating
        customer_crud.edit_customer_rating_data(db, db_customer.get_customer_id, rating)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_customer = None
        error_msg = 'change_customer_rating_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer}


def get_customer_rating_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_customer_rating = customer_crud.get_customer_rating_by_id(db, id)
        if db_customer_rating is None:
            status = 418
            error_msg = 'get_customer_rating_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer_rating = None
        error_msg = 'get_customer_rating_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer_rating}


def get_customer_rating_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_customer_rating = customer_crud.get_customer_rating_active_list(db)
        if db_customer_rating is None:
            status = 418
            error_msg = 'get_customer_rating_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer_rating = None
        error_msg = 'get_customer_rating_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer_rating}


def get_customer_rating_active_list_by_set_customer(db: Session, set_customer_id):
    try:
        status = 200
        error_msg = ''
        db_customer_rating = customer_crud \
            .get_customer_rating_active_list_by_set_customer(db, set_customer_id)
        if db_customer_rating is None:
            status = 418
            error_msg = 'get_customer_rating_active_list_by_set_customer_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer_rating = None
        error_msg = 'get_customer_rating_active_list_by_set_customer_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer_rating}


def get_customer_rating_active_list_by_get_customer(db: Session, get_customer_id):
    try:
        status = 200
        error_msg = ''
        db_customer_rating = customer_crud \
            .get_customer_rating_active_list_by_get_customer(db, get_customer_id)
        if db_customer_rating is None:
            status = 418
            error_msg = 'get_customer_rating_active_list_by_get_customer_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer_rating = None
        error_msg = 'get_customer_rating_active_list_by_get_customer_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer_rating}


def search_customer_rating_active_by_get_customer(db: Session, get_customer_id, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_customer_rating = customer_crud \
            .search_customer_rating_active_by_get_customer(db, get_customer_id, search_text)
        if db_customer_rating is None:
            status = 418
            error_msg = 'search_customer_rating_active_by_get_customer_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_customer_rating = None
        error_msg = 'search_customer_rating_active_by_get_customer_error'
    return {"status": status, "error_msg": error_msg, "result": db_customer_rating}


# endregion


# region Logs
def get_customer_log_list_customer_id(db: Session, customer_id):
    try:
        status = 200
        error_msg = ''
        db_log = customer_crud.get_customer_log_list_customer_id(db, customer_id)
        if db_log is None:
            status = 418
            error_msg = 'get_customer_log_list_customer_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_log = None
        error_msg = 'get_customer_log_list_customer_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_log}


def get_customer_balance_log_list_customer_balance_id(db: Session, customer_balance_id):
    try:
        status = 200
        error_msg = ''
        db_log = customer_crud.get_customer_balance_log_list_customer_balance_id(db, customer_balance_id)
        if db_log is None:
            status = 418
            error_msg = 'get_customer_balance_log_list_customer_balance_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_log = None
        error_msg = 'get_customer_balance_log_list_customer_balance_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_log}

# endregion
