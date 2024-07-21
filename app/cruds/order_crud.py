import datetime
import json
import uuid
from datetime import datetime
from sqlalchemy import and_

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, or_, not_
from sqlalchemy.orm import Session, aliased

from app import models


# region Samples to use
def order_view_sample(db: Session):
    driver = aliased(models.Customers)
    join_query = db.query(models.Orders.id,
                          models.Orders.driver_id,
                          models.Orders.vehicle_id,
                          models.Orders.client_id,
                          models.Orders.service_id,
                          models.Orders.shift_id,
                          models.Orders.rate_id,
                          models.Orders.district_id_from,
                          models.Orders.district_id_to,
                          models.Orders.order_address_from,
                          models.Orders.order_address_to,
                          models.Orders.order_code,
                          models.Orders.order_desc,
                          models.Orders.order_date,
                          models.Orders.order_type,
                          models.Orders.order_state,
                          models.Orders.pay_total,
                          models.Orders.pay_discount_prc,
                          models.Orders.pay_discount_amount,
                          models.Orders.pay_net_total,
                          models.Orders.pay_net_total_text,
                          models.Orders.service_prc,
                          models.Orders.service_amount,
                          models.Orders.order_distance,
                          models.Orders.order_time,
                          models.Orders.order_wait_time,
                          models.Orders.canceled_vehicles,
                          models.Orders.order_user,
                          models.Orders.create_user,
                          models.Orders.state,
                          models.Orders.create_ts,
                          models.Orders.update_ts,
                          models.Customers.fullname,
                          models.Customers.discount_percent,
                          models.Customers.discount_limit,
                          models.Customers.phone,
                          driver.fullname.label('driver_fullname'),
                          models.Services.service_name,
                          models.Shifts.shift_name,
                          models.Vehicles.vehicle_name,
                          models.Rates.price_km,
                          models.Rates.price_min,
                          models.Rates.price_wait_min,
                          models.Rates.minute_free_wait,
                          models.Rates.km_free,
                          models.Rates.price_delivery,
                          models.Rates.minute_for_wait,
                          models.Rates.price_cancel,
                          models.Rates.price_minimal) \
        .outerjoin(models.Customers, models.Customers.id == models.Orders.client_id) \
        .outerjoin(driver, driver.id == models.Orders.driver_id) \
        .outerjoin(models.Vehicles, models.Vehicles.id == models.Orders.vehicle_id) \
        .outerjoin(models.Services, models.Services.id == models.Orders.service_id) \
        .outerjoin(models.Shifts, models.Shifts.id == models.Orders.shift_id) \
        .outerjoin(models.Rates, models.Rates.id == models.Orders.rate_id)
    return join_query


def order_history_view_sample(db: Session):
    join_query = db.query(models.OrderHistory.id,
                          models.OrderHistory.order_id,
                          models.OrderHistory.order_date,
                          models.OrderHistory.order_state,
                          models.OrderHistory.action_user,
                          models.OrderHistory.create_ts,
                          models.Customers.fullname) \
        .outerjoin(models.Customers, models.Customers.username == models.OrderHistory.action_user)
    return join_query


# endregion


# region Order
def add_order(db: Session, driver_id, vehicle_id, client_id, service_id, shift_id, rate_id, district_id_from,
              district_id_to, order_address_from, order_address_to, order_code, order_desc, order_date, order_type,
              order_state, pay_discount_prc, pay_discount_amount, service_prc, create_user):
    db_order = models.Orders(id=uuid.uuid4(),
                             driver_id=driver_id,
                             vehicle_id=vehicle_id,
                             client_id=client_id,
                             service_id=service_id,
                             shift_id=shift_id,
                             rate_id=rate_id,
                             district_id_from=district_id_from,
                             district_id_to=district_id_to,
                             order_address_from=order_address_from,
                             order_address_to=order_address_to,
                             order_code=order_code,
                             order_desc=order_desc,
                             order_date=order_date,
                             order_type=order_type,
                             order_state=order_state,
                             pay_discount_prc=pay_discount_prc,
                             pay_discount_amount=pay_discount_amount,
                             service_prc=service_prc,
                             canceled_vehicles=[],
                             create_user=create_user,
                             state=models.EntityState.active.name,
                             create_ts=datetime.now(),
                             update_ts=datetime.now())
    db.add(db_order)
    db.flush()
    order_json_info = {'driver_id': str(driver_id),
                       'vehicle_id': str(vehicle_id),
                       'client_id': str(client_id),
                       'service_id': str(service_id),
                       'district_id_from': str(district_id_from),
                       'district_id_to': str(district_id_to),
                       'order_code': str(order_code),
                       'order_desc': str(order_desc),
                       'order_date': str(order_date),
                       'order_type': str(order_type.name),
                       'order_state': str(order_state.name),
                       'pay_discount_prc': str(pay_discount_prc),
                       'pay_discount_amount': str(pay_discount_amount),
                       'service_prc': str(service_prc),
                       'create_user': str(create_user)}
    db_order_log = models.OrderLog(id=uuid.uuid4(),
                                   order_id=db_order.id,
                                   action=models.OrderAction.OrderAdd,
                                   action_user=create_user,
                                   sup_info=json.dumps(order_json_info),
                                   action_ts=datetime.now())
    db.add(db_order_log)
    return db_order


def add_order_driver(db: Session, id, driver_id, vehicle_id, action_user):
    db_order = db.query(models.Orders).filter(models.Orders.id == id)
    edit_order_crud = {
        models.Orders.driver_id: driver_id,
        models.Orders.vehicle_id: vehicle_id,
        models.Orders.update_ts: datetime.now()
    }
    db_order.update(edit_order_crud)
    order_json_info = {'driver_id': str(driver_id),
                       'vehicle_id': str(vehicle_id)}
    db_order_log = models.OrderLog(id=uuid.uuid4(),
                                   order_id=id,
                                   action=models.OrderAction.OrderDriverChange,
                                   action_user=action_user,
                                   sup_info=json.dumps(order_json_info),
                                   action_ts=datetime.now())
    db.add(db_order_log)
    return id


def change_order_driver(db: Session, id, driver_id, vehicle_id, action_user):
    db_order = db.query(models.Orders).filter(models.Orders.id == id)
    edit_order_crud = {
        models.Orders.driver_id: driver_id,
        models.Orders.vehicle_id: vehicle_id,
        models.Orders.order_state: models.OrderState.taken,
        models.Orders.update_ts: datetime.now()
    }
    db_order.update(edit_order_crud)
    order_json_info = {'driver_id': str(driver_id),
                       'vehicle_id': str(vehicle_id)}
    db_order_log = models.OrderLog(id=uuid.uuid4(),
                                   order_id=id,
                                   action=models.OrderAction.OrderDriverChange,
                                   action_user=action_user,
                                   sup_info=json.dumps(order_json_info),
                                   action_ts=datetime.now())
    db.add(db_order_log)
    return id


def remove_order_driver(db: Session, id, action_user):
    db_order = db.query(models.Orders).filter(models.Orders.id == id)
    edit_order_crud = {
        models.Orders.driver_id: None,
        models.Orders.vehicle_id: None,
        models.Orders.order_state: models.OrderState.created,
        models.Orders.update_ts: datetime.now()
    }
    db_order.update(edit_order_crud)
    order_json_info = {'driver_id': '',
                       'vehicle_id': ''}
    db_order_log = models.OrderLog(id=uuid.uuid4(),
                                   order_id=id,
                                   action=models.OrderAction.OrderDriverRemove,
                                   action_user=action_user,
                                   sup_info=json.dumps(order_json_info),
                                   action_ts=datetime.now())
    db.add(db_order_log)
    return id


def reject_order(db: Session, id, canceled_vehicles, action_user):
    db_order = db.query(models.Orders).filter(models.Orders.id == id)
    edit_order_crud = {
        models.Orders.driver_id: None,
        models.Orders.vehicle_id: None,
        models.Orders.canceled_vehicles: canceled_vehicles,
        models.Orders.update_ts: datetime.now()
    }
    db_order.update(edit_order_crud)
    order_json_info = {'driver_id': '',
                       'vehicle_id': ''}
    db_order_log = models.OrderLog(id=uuid.uuid4(),
                                   order_id=id,
                                   action=models.OrderAction.OrderDriverChange,
                                   action_user=action_user,
                                   sup_info=json.dumps(order_json_info),
                                   action_ts=datetime.now())
    db.add(db_order_log)
    return id


def change_order_state(db: Session, id, order_state, action_user):
    db_order = db.query(models.Orders).filter(models.Orders.id == id)
    edit_order_crud = {
        models.Orders.order_state: order_state,
        models.Orders.update_ts: datetime.now()
    }
    db_order.update(edit_order_crud)
    order_json_info = {'order_state': str(order_state)}
    db_order_log = models.OrderLog(id=uuid.uuid4(),
                                   order_id=id,
                                   action=models.OrderAction.OrderStateChange,
                                   action_user=action_user,
                                   sup_info=json.dumps(order_json_info),
                                   action_ts=datetime.now())
    db.add(db_order_log)
    return id


def accept_order(db: Session, id, action_user):
    db_order = db.query(models.Orders).filter(models.Orders.id == id)
    edit_order_crud = {
        models.Orders.order_state: models.OrderState.taken,
        models.Orders.order_user: action_user,
        models.Orders.update_ts: datetime.now()
    }
    db_order.update(edit_order_crud)
    order_json_info = {'order_state': str(models.OrderState.taken.name),
                       'order_user': action_user}
    db_order_log = models.OrderLog(id=uuid.uuid4(),
                                   order_id=id,
                                   action=models.OrderAction.OrderStateChange,
                                   action_user=action_user,
                                   sup_info=json.dumps(order_json_info),
                                   action_ts=datetime.now())
    db.add(db_order_log)
    return id


def take_postponed_order(db: Session, id, driver_id, vehicle_id, action_user):
    db_order = db.query(models.Orders).filter(models.Orders.id == id)
    edit_order_crud = {
        models.Orders.driver_id: driver_id,
        models.Orders.vehicle_id: vehicle_id,
        models.Orders.order_state: models.OrderState.taken_post,
        models.Orders.order_user: action_user,
        models.Orders.update_ts: datetime.now()
    }
    db_order.update(edit_order_crud)
    order_json_info = {'driver_id': str(driver_id),
                       'vehicle_id': str(vehicle_id),
                       'order_state': str(models.OrderState.taken_post.name),
                       'order_user': action_user}
    db_order_log = models.OrderLog(id=uuid.uuid4(),
                                   order_id=id,
                                   action=models.OrderAction.OrderStateChange,
                                   action_user=action_user,
                                   sup_info=json.dumps(order_json_info),
                                   action_ts=datetime.now())
    db.add(db_order_log)
    return id


def finish_order(db: Session, id, pay_total, pay_net_total, pay_net_total_text, service_amount, order_distance,
                 order_time, order_wait_time, action_user):
    db_order = db.query(models.Orders).filter(models.Orders.id == id)
    edit_order_crud = {
        models.Orders.pay_total: pay_total,
        models.Orders.pay_net_total: pay_net_total,
        models.Orders.pay_net_total_text: pay_net_total_text,
        models.Orders.service_amount: service_amount,
        models.Orders.order_distance: order_distance,
        models.Orders.order_time: order_time,
        models.Orders.order_wait_time: order_wait_time,
        models.Orders.order_state: models.OrderState.finished,
        models.Orders.update_ts: datetime.now()
    }
    db_order.update(edit_order_crud)
    order_json_info = {'pay_total': str(pay_total),
                       'pay_net_total': str(pay_net_total),
                       'pay_net_total_text': str(pay_net_total_text),
                       'service_amount': str(service_amount),
                       'order_distance': str(order_distance),
                       'order_time': str(order_time),
                       'order_wait_time': str(order_wait_time),
                       'order_state': str(models.OrderState.finished.name)}
    db_order_log = models.OrderLog(id=uuid.uuid4(),
                                   order_id=id,
                                   action=models.OrderAction.OrderStateChange,
                                   action_user=action_user,
                                   sup_info=json.dumps(order_json_info),
                                   action_ts=datetime.now())
    db.add(db_order_log)
    return id


def get_order_by_id(db: Session, id):
    db_order = order_view_sample(db) \
        .filter(models.Orders.id == id).first()
    return db_order


def get_order_by_id_sample(db: Session, id):
    db_order = db.query(models.Orders).get(id)
    return db_order


def get_order_new_by_driver(db: Session, driver_id, vehicle_id):
    db_order = order_view_sample(db) \
        .filter(models.Orders.driver_id == driver_id) \
        .filter(models.Orders.vehicle_id == vehicle_id) \
        .filter(and_(models.Orders.order_state != models.OrderState.finished,
                     models.Orders.order_state != models.OrderState.canceled)) \
        .filter(models.Orders.order_state != models.OrderState.taken_post) \
        .order_by(models.Orders.create_ts)
    return db_order.first()


def get_order_new_by_driver_standart(db: Session, driver_id, vehicle_id):
    db_order = db.query(models.Orders) \
        .filter(models.Orders.driver_id == driver_id) \
        .filter(models.Orders.vehicle_id == vehicle_id) \
        .filter(models.Orders.order_type == models.OrderType.standart) \
        .filter(and_(models.Orders.order_state != models.OrderState.finished,
                     models.Orders.order_state != models.OrderState.canceled)) \
        .order_by(models.Orders.create_ts)
    return db_order.first()


def get_order_new_by_info(db: Session, service_ids, district_id, vehicle_id):
    db_order = order_view_sample(db) \
        .filter(models.Orders.driver_id == None) \
        .filter(models.Orders.vehicle_id == None) \
        .filter(models.Orders.service_id.in_(service_ids)) \
        .filter(models.Orders.district_id_from == district_id) \
        .filter(models.Orders.order_type == models.OrderType.standart) \
        .filter(models.Orders.order_state == models.OrderState.created) \
        .filter(not_(models.Orders.canceled_vehicles.any(str(vehicle_id)))) \
        .order_by(models.Orders.create_ts)
    return db_order.first()


def get_order_new_by_service(db: Session, service_ids, vehicle_id):
    db_order = order_view_sample(db) \
        .filter(models.Orders.driver_id == None) \
        .filter(models.Orders.vehicle_id == None) \
        .filter(models.Orders.service_id.in_(service_ids)) \
        .filter(models.Orders.order_type == models.OrderType.standart) \
        .filter(models.Orders.order_state == models.OrderState.created) \
        .filter(not_(models.Orders.canceled_vehicles.any(str(vehicle_id)))) \
        .order_by(models.Orders.create_ts)
    return db_order.first()


def get_order_post_list_by_driver(db: Session, driver_id, vehicle_id):
    db_order = db.query(models.Orders) \
        .filter(or_(models.Orders.driver_id == driver_id,
                    models.Orders.driver_id == None)) \
        .filter(or_(models.Orders.vehicle_id == vehicle_id,
                    models.Orders.vehicle_id == None)) \
        .filter(models.Orders.order_type == models.OrderType.postponed) \
        .filter(models.Orders.order_state == models.OrderState.created) \
        .order_by(models.Orders.create_ts)
    return db_order.all()


def get_order_post_list_by_info(db: Session, driver_id, vehicle_id, service_ids, district_id):
    db_order = db.query(models.Orders) \
        .filter(or_(models.Orders.driver_id == driver_id,
                    models.Orders.driver_id == None)) \
        .filter(or_(models.Orders.vehicle_id == vehicle_id,
                    models.Orders.vehicle_id == None)) \
        .filter(models.Orders.service_id.in_(service_ids)) \
        .filter(models.Orders.district_id_from == district_id) \
        .filter(models.Orders.order_type == models.OrderType.postponed) \
        .filter(models.Orders.order_state == models.OrderState.created) \
        .order_by(models.Orders.create_ts)
    return db_order.all()


def get_order_post_list_by_service(db: Session, service_ids):
    db_order = order_view_sample(db) \
        .filter(models.Orders.driver_id == None) \
        .filter(models.Orders.vehicle_id == None) \
        .filter(models.Orders.service_id.in_(service_ids)) \
        .filter(models.Orders.order_type == models.OrderType.postponed) \
        .filter(models.Orders.order_state == models.OrderState.created) \
        .order_by(models.Orders.create_ts)
    return db_order.all()


def get_order_post_list_by_info_service(db: Session, driver_id, vehicle_id, service_ids):
    db_order = order_view_sample(db) \
        .filter(models.Orders.driver_id == driver_id) \
        .filter(models.Orders.vehicle_id == vehicle_id) \
        .filter(models.Orders.service_id.in_(service_ids)) \
        .filter(models.Orders.order_type == models.OrderType.postponed) \
        .filter(models.Orders.order_state != models.OrderState.finished) \
        .filter(models.Orders.order_state != models.OrderState.canceled) \
        .order_by(models.Orders.create_ts.desc())
    return db_order.all()


def count_orders_standart(db: Session, current_date):
    db_order = db.query(models.Orders) \
        .filter(func.date(models.Orders.order_date) == func.date(current_date)) \
        .filter(models.Orders.order_type == models.OrderType.standart) \
        .filter(models.Orders.state == models.EntityState.active)
    return db_order.count()


def count_orders_postponed(db: Session, current_date):
    db_order = db.query(models.Orders) \
        .filter(func.date(models.Orders.order_date) == func.date(current_date)) \
        .filter(models.Orders.order_type == models.OrderType.postponed) \
        .filter(models.Orders.state == models.EntityState.active)
    return db_order.count()


def count_orders_waiting(db: Session):
    db_order = db.query(models.Orders) \
        .filter(models.Orders.order_state == models.OrderState.created) \
        .filter(models.Orders.state == models.EntityState.active)
    return db_order.count()


def search_active_by_info(db: Session, order_type, order_state, service_id, start_date, end_date, search_text):
    db_order = order_view_sample(db) \
        .filter(models.Orders.state == models.EntityState.active)
    if order_type:
        db_order = db_order.filter(models.Orders.order_type == order_type)
    if order_state:
        db_order = db_order.filter(models.Orders.order_state == order_state)
    if service_id:
        db_order = db_order.filter(models.Orders.service_id == service_id)
    if start_date:
        db_order = db_order.filter(models.Orders.order_date >= start_date)
    if end_date:
        db_order = db_order.filter(models.Orders.order_date < end_date)
    db_order = db_order.filter(func.concat(models.Orders.order_code,
                                           ' ', models.Orders.order_desc,
                                           ' ', models.Customers.phone,
                                           ' ', func.to_char(models.Orders.order_date, "DD.MM.YYYY")).ilike(
        '%' + search_text + '%')) \
        .order_by(models.Orders.create_ts.desc())
    return paginate(db_order)


def search_active_by_driver(db: Session, driver_id, order_type, order_state, service_id, start_date, end_date,
                            search_text):
    db_order = order_view_sample(db) \
        .filter(models.Orders.order_state != models.OrderState.canceled) \
        .filter(models.Orders.state == models.EntityState.active) \
        .filter(models.Orders.driver_id == driver_id)
    if order_type:
        db_order = db_order.filter(models.Orders.order_type == order_type)
    if order_state:
        db_order = db_order.filter(models.Orders.order_state == order_state)
    if service_id:
        db_order = db_order.filter(models.Orders.service_id == service_id)
    if start_date:
        db_order = db_order.filter(models.Orders.order_date >= start_date)
    if end_date:
        db_order = db_order.filter(models.Orders.order_date < end_date)
    db_order = db_order.filter(func.concat(models.Orders.order_code,
                                           ' ', models.Orders.order_desc,
                                           ' ', func.to_char(models.Orders.order_date, "DD.MM.YYYY")).ilike(
        '%' + search_text + '%')) \
        .order_by(models.Orders.create_ts.desc())
    return paginate(db_order)


def search_active_by_client(db: Session, client_id, order_type, order_state, service_id, start_date, end_date,
                            search_text):
    db_order = order_view_sample(db) \
        .filter(models.Orders.state == models.EntityState.active) \
        .filter(models.Orders.client_id == client_id)
    if order_type:
        db_order = db_order.filter(models.Orders.order_type == order_type)
    if order_state:
        db_order = db_order.filter(models.Orders.order_state == order_state)
    if service_id:
        db_order = db_order.filter(models.Orders.service_id == service_id)
    if start_date:
        db_order = db_order.filter(models.Orders.order_date >= start_date)
    if end_date:
        db_order = db_order.filter(models.Orders.order_date < end_date)
    db_order = db_order.filter(func.concat(models.Orders.order_code,
                                           ' ', models.Orders.order_desc,
                                           ' ', func.to_char(models.Orders.order_date, "DD.MM.YYYY")).ilike(
        '%' + search_text + '%')) \
        .order_by(models.Orders.create_ts.desc())
    return paginate(db_order)


# endregion

# region Order History
def add_order_history(db: Session, order_id, order_date, order_state, action_user):
    db_order = models.OrderHistory(id=uuid.uuid4(),
                                   order_id=order_id,
                                   order_date=order_date,
                                   order_state=order_state,
                                   action_user=action_user,
                                   create_ts=datetime.now(),
                                   update_ts=datetime.now())
    db.add(db_order)
    return db_order


def get_order_history_list_by_order(db: Session, order_id):
    db_order = order_history_view_sample(db) \
        .filter(models.OrderHistory.order_id == order_id) \
        .order_by(models.OrderHistory.create_ts)
    return db_order.all()
# endregion
