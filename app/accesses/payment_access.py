import datetime
import logging
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import FlushError

from app.accesses import temp_access, customer_access
from app.cruds import payment_crud

log = logging.getLogger(__name__)


# region Payment
def add_payment(db: Session, payment_method, customer_id, payment_amount, payment_desc, payment_date, in_out,
                create_user):
    try:
        status = 200
        error_msg = ''
        if payment_date is None:
            payment_date = datetime.now()
        payment_code = temp_access.create_payment_code()
        payment_amount_text = temp_access.num2ru(payment_amount)
        db_payment = payment_crud.add_payment(db, payment_method, customer_id, payment_code, payment_amount,
                                              payment_amount_text, payment_desc, payment_date, in_out, create_user)
        if db_payment is None:
            status = 418
            error_msg = 'add_payment_failed'
        customer_access.add_balance_to_customer(db, customer_id, payment_amount, in_out, 0, create_user)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        db_payment = None
        error_msg = 'add_payment_error'
    return {"status": status, "error_msg": error_msg, "result": db_payment}


def edit_payment(db: Session, id, payment_method, customer_id, payment_amount, payment_desc, payment_date, in_out,
                 create_user):
    try:
        status = 200
        error_msg = ''
        db_payment_old = payment_crud.get_payment_by_id_sample(db, id)
        payment_amount_old = db_payment_old.payment_amount
        payment_amount_text = temp_access.num2ru(payment_amount)
        db_payment = payment_crud.edit_payment(db, id, payment_method, customer_id, payment_amount, payment_amount_text,
                                               payment_desc, payment_date, in_out, create_user)
        if db_payment is None:
            status = 418
            error_msg = 'edit_payment_failed'
        customer_access.add_balance_to_customer(db, customer_id, payment_amount, in_out, payment_amount_old,
                                                create_user)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        db_payment = None
        error_msg = 'edit_payment_error'
    return {"status": status, "error_msg": error_msg, "result": db_payment}


def edit_payment_amount(db: Session, id, payment_amount, create_user):
    try:
        status = 200
        error_msg = ''
        db_payment_old = payment_crud.get_payment_by_id_sample(db, id)
        payment_amount_old = db_payment_old.payment_amount
        customer_id = db_payment_old.customer_id
        in_out = db_payment_old.in_out
        payment_amount_text = temp_access.num2ru(payment_amount)
        db_payment = payment_crud.edit_payment_amount(db, id, payment_amount, payment_amount_text, create_user)
        if db_payment is None:
            status = 418
            error_msg = 'edit_payment_amount_failed'
        customer_access.add_balance_to_customer(db, customer_id, payment_amount, in_out, payment_amount_old,
                                                create_user)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        db_payment = None
        error_msg = 'edit_payment_amount_error'
    return {"status": status, "error_msg": error_msg, "result": db_payment}


def change_payment_state(db: Session, id, state, create_user):
    try:
        status = 200
        error_msg = ''
        db_payment_old = payment_crud.get_payment_by_id_sample(db, id)
        payment_amount = db_payment_old.payment_amount
        customer_id = db_payment_old.customer_id
        in_out = db_payment_old.in_out
        db_payment = payment_crud.change_payment_state(db, id, state, create_user)
        if db_payment is None:
            status = 418
            error_msg = 'change_payment_state_failed'
        customer_access.add_balance_to_customer(db, customer_id, 0, in_out, payment_amount, create_user)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        db_payment = None
        error_msg = 'change_payment_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_payment}


def get_payment_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_payment = payment_crud.get_payment_by_id(db, id)
        if db_payment is None:
            status = 418
            error_msg = 'get_payment_detail_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_payment = None
        error_msg = 'get_payment_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_payment}


def search_active_by_info(db: Session, payment_method, in_out, start_date, end_date, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_payment = payment_crud.search_active_by_info(db, payment_method, in_out, start_date, end_date,
                                                        search_text)
        if db_payment is None:
            status = 418
            error_msg = 'search_active_by_info_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_payment = None
        error_msg = 'search_active_by_info_error'
    return {"status": status, "error_msg": error_msg, "result": db_payment}


def search_active_by_customer(db: Session, customer_id, payment_method, in_out, start_date, end_date, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_payment = payment_crud.search_active_by_customer(db, customer_id, payment_method, in_out, start_date,
                                                            end_date, search_text)
        if db_payment is None:
            status = 418
            error_msg = 'search_active_by_customer_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_payment = None
        error_msg = 'search_active_by_customer_error'
    return {"status": status, "error_msg": error_msg, "result": db_payment}
# endregion
