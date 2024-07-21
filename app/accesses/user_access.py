import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from app import config, models
from app.accesses import token_access, temp_access, customer_access
from app.cruds import user_crud, customer_crud

log = logging.getLogger(__name__)

static_path = config.IMAGE_FULL_URL + '/avatars'
static_image_path = config.IMAGE_URL + '/avatars'


# region Users
def get_user(db: Session, username: str):
    db_user = user_crud.get_active_user_by_username(db, username)
    if db_user is None:
        return None
    return db_user


def add_user(db: Session, username, password, role, image, customer_id, action_user):
    try:
        create_image = temp_access.create_image(image, 'no-image', static_path)
        status = create_image["status"]
        error_msg = create_image["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": create_image["result"]}
        imagename = create_image["result"]["imagename"]
        destination_image = ''
        if imagename and imagename != 'no-image':
            destination_image = static_image_path + '/' + imagename
        hash_password = token_access.get_password_hash(password)
        db_user = user_crud.add_user(db, username, hash_password, role, imagename, destination_image, action_user)
        if db_user is None:
            status = 418
            error_msg = 'add_user_failed'
        if db_user and customer_id:
            db_customer = customer_access.add_user_to_customer(db, username, customer_id, action_user)
            status = db_customer["status"]
            error_msg = db_customer["error_msg"]
            if status == 418:
                return {"status": status, "error_msg": error_msg, "result": db_customer["result"]}
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_user = None
        error_msg = 'add_user_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


async def add_client(db: Session, phone, lang, phone_code):
    try:
        status = 200
        error_msg = ''
        if len(phone) != 12:
            status = 418
            db_user = None
            error_msg = 'wrong_phone_number_format'
            return {"status": status, "error_msg": error_msg, "result": db_user}
        from app.routers import websocket
        password = await websocket.new_user_sms(phone, lang, phone_code)
        hash_password = token_access.get_password_hash(password)
        db_user = user_crud.get_user_detail_by_username(db, phone)
        if db_user is None:
            db_user = user_crud.add_user(db, phone, hash_password, models.UserRole.user, 'no-image', 'no-image', None)
            if db_user is None:
                status = 418
                error_msg = 'add_user_failed'
        else:
            if db_user.state != models.UserState.enabled:
                user_crud.change_user_state(db, phone, models.UserState.enabled, None)
            user_crud.change_user_password(db, phone, hash_password, None)
        db_client = customer_crud.get_customer_by_phone(db, phone)
        if db_client is None:
            customer_type = models.CustomerType.client
            code = temp_access.create_user_code(customer_type)
            client_id = customer_crud.add_customer(db, phone, phone, None, None, None, models.GenderType.man,
                                                   customer_type, code, 0, 0, None, phone, None, None, None, None, None)
        else:
            client_id = db_client.id
        if db_user and client_id:
            db_customer = customer_access.add_user_to_customer(db, phone, client_id, None)
            status = db_customer["status"]
            error_msg = db_customer["error_msg"]
            if status == 418:
                return {"status": status, "error_msg": error_msg, "result": db_customer["result"]}
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        db.rollback()
        status = 418
        db_user = None
        error_msg = 'add_user_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


def edit_user(db: Session, username, role, customer_id, image, action_user):
    try:
        user = get_user_by_username(db, username)
        status = user["status"]
        error_msg = user["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": user["result"]}
        old_customer_id = user["result"].id
        if image:
            create_image = temp_access.create_image(image, 'no-image', static_path)
            status = create_image["status"]
            error_msg = create_image["error_msg"]
            if status == 418:
                return {"status": status, "error_msg": error_msg, "result": create_image["result"]}
            imagename = create_image["result"]["imagename"]
            destination_image = static_image_path + '/' + imagename
        else:
            imagename = user["result"].avatar_name
            destination_image = user["result"].avatar_path
        db_user = user_crud.edit_user(db, username, role, imagename, destination_image, action_user)
        if db_user is None:
            status = 418
            error_msg = 'edit_user_failed'
        if db_user and customer_id:
            if old_customer_id != customer_id:
                db_customer = customer_access.add_user_to_customer(db, username, customer_id, action_user)
                status = db_customer["status"]
                error_msg = db_customer["error_msg"]
                if status == 418:
                    return {"status": status, "error_msg": error_msg, "result": db_customer["result"]}
                if old_customer_id:
                    db_customer = customer_access.add_user_to_customer(db, None, old_customer_id, action_user)
                    status = db_customer["status"]
                    error_msg = db_customer["error_msg"]
                    if status == 418:
                        return {"status": status, "error_msg": error_msg, "result": db_customer["result"]}
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_user = None
        error_msg = 'edit_user_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


def change_user_password(db: Session, username, password, action_user):
    try:
        user = get_user_by_username(db, username)
        status = user["status"]
        error_msg = user["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": user["result"]}
        hash_password = token_access.get_password_hash(password)
        db_user = user_crud.change_user_password(db, username, hash_password, action_user)
        if db_user is None:
            status = 418
            error_msg = 'change_user_password_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_user = None
        error_msg = 'change_user_password_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


def change_user_role(db: Session, username, role, action_user):
    try:
        user = get_user_by_username(db, username)
        status = user["status"]
        error_msg = user["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": user["result"]}
        db_user = user_crud.change_user_role(db, username, role, action_user)
        if db_user is None:
            status = 418
            error_msg = 'change_user_role_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_user = None
        error_msg = 'change_user_role_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


def change_user_state(db: Session, username, state, action_user):
    try:
        user = get_user_by_username(db, username)
        status = user["status"]
        error_msg = user["error_msg"]
        if status == 418:
            return {"status": status, "error_msg": error_msg, "result": user["result"]}
        db_user = user_crud.change_user_state(db, username, state, action_user)
        if db_user is None:
            status = 418
            error_msg = 'change_user_state_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, action_user)
        db.rollback()
        status = 418
        db_user = None
        error_msg = 'change_user_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


def get_user_by_username(db: Session, username):
    try:
        status = 200
        error_msg = ''
        db_user = user_crud.get_user_by_username(db, username)
        if db_user is None:
            status = 418
            error_msg = 'get_user_detail_by_username_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_user = None
        error_msg = 'get_user_detail_by_username_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


def get_user_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_user = user_crud.get_user_list(db)
        if db_user is None:
            status = 418
            error_msg = 'get_user_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_user = None
        error_msg = 'get_user_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


def get_user_active_list(db: Session):
    try:
        status = 200
        error_msg = ''
        db_user = user_crud.get_user_active_list(db)
        if db_user is None:
            status = 418
            error_msg = 'get_user_active_list_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_user = None
        error_msg = 'get_user_active_list_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


def search(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_user = user_crud.search(db, search_text)
        if db_user is None:
            status = 418
            error_msg = 'search_user_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_user = None
        error_msg = 'search_user_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


def search_active(db: Session, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_user = user_crud.search_active(db, search_text)
        if db_user is None:
            status = 418
            error_msg = 'search_active_user_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_user = None
        error_msg = 'search_active_user_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


def search_active_type(db: Session, search_text, customer_type):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_user = user_crud.search_active_type(db, search_text, customer_type)
        if db_user is None:
            status = 418
            error_msg = 'search_active_type_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_user = None
        error_msg = 'search_active_type_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


def get_user_action_log_list_by_username(db: Session, username):
    try:
        status = 200
        error_msg = ''
        db_user = user_crud.get_user_action_log_list_by_username(db, username)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_user = None
        error_msg = 'get_user_action_log_list_by_username_error'
    return {"status": status, "error_msg": error_msg, "result": db_user}


def log_out(db: Session, username):
    try:
        status = 200
        error_msg = ''
        db_user = user_crud.add_user_action_log(db, username, models.UserAction.UserLogOut, None, None, None, None,
                                                None)
        if db_user is None:
            status = 418
            error_msg = 'user_log_out_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        error_msg = 'user_log_out_error'
    return {"status": status, "error_msg": error_msg, "result": None}


# endregion


# region Logs
def get_user_log_list_username(db: Session, username):
    try:
        status = 200
        error_msg = ''
        db_log = user_crud.get_user_log_list_username(db, username)
        if db_log is None:
            status = 418
            error_msg = 'get_user_log_list_username_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_log = None
        error_msg = 'get_user_log_list_username_error'
    return {"status": status, "error_msg": error_msg, "result": db_log}


def get_user_action_log_list_username(db: Session, username):
    try:
        status = 200
        error_msg = ''
        db_log = user_crud.get_user_action_log_list_username(db, username)
        if db_log is None:
            status = 418
            error_msg = 'get_user_action_log_list_user_action_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_log = None
        error_msg = 'get_user_action_log_list_user_action_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_log}
# endregion
