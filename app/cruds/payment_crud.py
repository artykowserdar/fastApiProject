import datetime
import json
import uuid
from datetime import datetime

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models


# region Samples to use
def payment_view_sample(db: Session):
    join_query = db.query(models.Payments.id,
                          models.Payments.payment_method,
                          models.Payments.customer_id,
                          models.Payments.payment_code,
                          models.Payments.payment_amount,
                          models.Payments.payment_amount_text,
                          models.Payments.payment_date,
                          models.Payments.payment_desc,
                          models.Payments.in_out,
                          models.Payments.create_user,
                          models.Payments.state,
                          models.Payments.create_ts,
                          models.Payments.update_ts,
                          models.Customers.fullname,
                          models.Customers.phone) \
        .outerjoin(models.Customers, models.Customers.id == models.Payments.customer_id)
    return join_query


# endregion


# region Payment
def add_payment(db: Session, payment_method, customer_id, payment_code, payment_amount, payment_amount_text,
                payment_desc, payment_date, in_out, create_user):
    db_payment = models.Payments(id=uuid.uuid4(),
                                 payment_method=payment_method,
                                 customer_id=customer_id,
                                 payment_code=payment_code,
                                 payment_amount=payment_amount,
                                 payment_amount_text=payment_amount_text,
                                 payment_desc=payment_desc,
                                 payment_date=payment_date,
                                 in_out=in_out,
                                 create_user=create_user,
                                 state=models.EntityState.active,
                                 create_ts=datetime.now(),
                                 update_ts=datetime.now())
    db.add(db_payment)
    db.flush()
    payment_json_info = {'payment_method': str(payment_method),
                         'customer_id': str(customer_id),
                         'payment_amount': str(payment_amount),
                         'payment_amount_text': str(payment_amount_text),
                         'payment_code': str(payment_code),
                         'payment_desc': str(payment_desc),
                         'payment_date': str(payment_date),
                         'in_out': str(in_out),
                         'create_user': str(create_user)}
    db_payment_log = models.PaymentLog(id=uuid.uuid4(),
                                       payment_id=db_payment.id,
                                       action=models.PaymentAction.PaymentAdd,
                                       action_user=create_user,
                                       sup_info=json.dumps(payment_json_info),
                                       action_ts=datetime.now())
    db.add(db_payment_log)
    return db_payment.id


def edit_payment(db: Session, id, payment_method, customer_id, payment_amount, payment_amount_text, payment_desc,
                 payment_date, in_out, action_user):
    db_payment = db.query(models.Payments).filter(models.Payments.id == id)
    edit_payment_crud = {
        models.Payments.payment_method: payment_method,
        models.Payments.customer_id: customer_id,
        models.Payments.payment_amount: payment_amount,
        models.Payments.payment_amount_text: payment_amount_text,
        models.Payments.payment_desc: payment_desc,
        models.Payments.payment_date: payment_date,
        models.Payments.in_out: in_out,
        models.Payments.update_ts: datetime.now()
    }
    db_payment.update(edit_payment_crud)
    payment_json_info = {'payment_method': str(payment_method.name),
                         'customer_id': str(customer_id),
                         'payment_amount': str(payment_amount),
                         'payment_amount_text': str(payment_amount_text),
                         'payment_desc': str(payment_desc),
                         'payment_date': str(payment_date),
                         'in_out': str(in_out)}
    db_payment_log = models.PaymentLog(id=uuid.uuid4(),
                                       payment_id=id,
                                       action=models.PaymentAction.PaymentEdit,
                                       action_user=action_user,
                                       sup_info=json.dumps(payment_json_info),
                                       action_ts=datetime.now())
    db.add(db_payment_log)
    return id


def edit_payment_amount(db: Session, id, payment_amount, payment_amount_text, action_user):
    db_payment = db.query(models.Payments).filter(models.Payments.id == id)
    edit_payment_crud = {
        models.Payments.payment_amount: payment_amount,
        models.Payments.payment_amount_text: payment_amount_text,
        models.Payments.update_ts: datetime.now()
    }
    db_payment.update(edit_payment_crud)
    payment_json_info = {'payment_amount': str(payment_amount),
                         'payment_amount_text': str(payment_amount_text)}
    db_payment_log = models.PaymentLog(id=uuid.uuid4(),
                                       payment_id=id,
                                       action=models.PaymentAction.PaymentEditPayment,
                                       action_user=action_user,
                                       sup_info=json.dumps(payment_json_info),
                                       action_ts=datetime.now())
    db.add(db_payment_log)
    return id


def change_payment_state(db: Session, id, state, action_user):
    db_payment = db.query(models.Payments).filter(models.Payments.id == id)
    edit_payment_crud = {
        models.Payments.state: state,
        models.Payments.update_ts: datetime.now()
    }
    db_payment.update(edit_payment_crud)
    payment_json_info = {'state': str(state.name)}
    db_payment_log = models.PaymentLog(id=uuid.uuid4(),
                                       payment_id=id,
                                       action=models.PaymentAction.PaymentStateChange,
                                       action_user=action_user,
                                       sup_info=json.dumps(payment_json_info),
                                       action_ts=datetime.now())
    db.add(db_payment_log)
    return id


def get_payment_by_id(db: Session, id):
    db_payment = payment_view_sample(db) \
        .filter(models.Payments.id == id).first()
    return db_payment


def get_payment_by_id_sample(db: Session, id):
    db_payment = db.query(models.Payments).get(id)
    return db_payment


def search_active_by_info(db: Session, payment_method, in_out, start_date, end_date, search_text):
    db_payment = payment_view_sample(db) \
        .filter(models.Payments.state == models.EntityState.active)
    if payment_method:
        db_payment = db_payment.filter(models.Payments.payment_method == payment_method)
    if in_out:
        db_payment = db_payment.filter(models.Payments.in_out == in_out)
    if start_date:
        db_payment = db_payment.filter(models.Payments.payment_date >= start_date)
    if end_date:
        db_payment = db_payment.filter(models.Payments.payment_date < end_date)
    db_payment = db_payment.filter(func.concat(models.Payments.payment_code,
                                               ' ', models.Payments.payment_desc,
                                               ' ', func.to_char(models.Payments.payment_date, "DD.MM.YYYY"))
                                   .ilike('%' + search_text + '%')) \
        .order_by(models.Payments.create_ts.desc())
    return paginate(db_payment)


def search_active_by_customer(db: Session, customer_id, payment_method, in_out, start_date, end_date, search_text):
    db_payment = payment_view_sample(db) \
        .filter(models.Payments.state == models.EntityState.active) \
        .filter(models.Payments.customer_id == customer_id)
    if payment_method:
        db_payment = db_payment.filter(models.Payments.payment_method == payment_method)
    if in_out:
        db_payment = db_payment.filter(models.Payments.in_out == in_out)
    if start_date:
        db_payment = db_payment.filter(models.Payments.payment_date >= start_date)
    if end_date:
        db_payment = db_payment.filter(models.Payments.payment_date < end_date)
    db_payment = db_payment.filter(func.concat(models.Payments.payment_code,
                                               ' ', models.Payments.payment_desc,
                                               ' ', func.to_char(models.Payments.payment_date, "DD.MM.YYYY"))
                                   .ilike('%' + search_text + '%')) \
        .order_by(models.Payments.create_ts.desc())
    return paginate(db_payment)

# endregion
