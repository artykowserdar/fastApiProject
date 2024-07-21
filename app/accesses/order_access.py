import datetime
import logging
from datetime import datetime

from num2words import num2words
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import FlushError

from app import models
from app.accesses import temp_access, customer_access, payment_access
from app.cruds import order_crud, vehicle_crud, temp_crud, customer_crud
from app.routers import websocket
from app.routers.websocket import manager

log = logging.getLogger(__name__)


# region Order
async def add_order(db: Session, vehicle_id, client_id, service_id, rate_id, shift_id, district_id_from, district_id_to,
                    address_from, address_to, coordinates_from, coordinates_to, order_desc, order_date,
                    pay_discount_prc, phone, fullname, create_user, lang="ru"):
    try:
        status = 200
        error_msg = ''
        canceled_vehicles = []
        today = datetime.now().date()
        driver_id = None
        if vehicle_id:
            db_vehicle = vehicle_crud.get_vehicle_by_id_simple(db, vehicle_id)
            driver_id = db_vehicle.driver_id
        db_rate = temp_crud.get_rate_by_id(db, rate_id)
        service_prc = db_rate.service_prc
        if client_id is None:
            db_customer = customer_crud.get_customer_by_phone(db, phone)
            if db_customer:
                client_id = db_customer.id
            else:
                if fullname is None:
                    fullname = phone
                customer_type = models.CustomerType.client
                code = temp_access.create_user_code(customer_type)
                client_id = customer_crud.add_customer(db, fullname, fullname, None, None, None, models.GenderType.man,
                                                       customer_type, code, 0, 0, None, phone, None, None, None, None,
                                                       create_user)
        else:
            db_customer = customer_crud.get_customer_by_id_sample(db, client_id)
            if db_customer.discount_percent > 0:
                pay_discount_prc = db_customer.discount_percent
            if db_customer.birth_date:
                if db_customer.birth_date.month == today.month and db_customer.birth_date.day == today.day:
                    pay_discount_prc = db_rate.birthday_discount_prc
        order_address_from = {"address": address_from,
                              "coordinates": coordinates_from}
        if address_to is None:
            address_to = ""
        order_address_to = {"address": address_to,
                            "coordinates": coordinates_to}
        if order_date:
            order_type = models.OrderType.postponed
        else:
            order_type = models.OrderType.standart
            order_date = datetime.now()
        pay_discount_amount = 0
        order_code = temp_access.create_order_code()
        order_state = models.OrderState.created
        db_order = order_crud.add_order(db, driver_id, vehicle_id, client_id, service_id, shift_id, rate_id,
                                        district_id_from, district_id_to, order_address_from, order_address_to,
                                        order_code, order_desc, order_date, order_type, order_state, pay_discount_prc,
                                        pay_discount_amount, service_prc, create_user)
        if db_order is None:
            status = 418
            error_msg = 'add_order_failed'
        order_crud.add_order_history(db, db_order.id, order_date, order_state, create_user)
        customer_access.add_client_address_history(db, client_id, district_id_from, models.AddressType.address_from,
                                                   address_from, coordinates_from, create_user)
        if address_to:
            customer_access.add_client_address_history(db, client_id, district_id_to, models.AddressType.address_to,
                                                       address_to, coordinates_to, create_user)
        await websocket.share_new_order(db, db_order.id, vehicle_id, driver_id, create_user, service_id,
                                        district_id_from, canceled_vehicles)
        await websocket.dashboard_statistics(db)
        await websocket.send_sms(db, db_order, lang)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        db_order = None
        error_msg = 'add_order_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


async def add_order_driver(db: Session, id, vehicle_id, create_user, lang="ru"):
    try:
        status = 200
        error_msg = ''
        order_data = order_crud.get_order_by_id(db, id)
        old_driver_id = order_data.driver_id
        old_vehicle_id = order_data.vehicle_id
        today = datetime.now()
        db_vehicle = vehicle_crud.get_vehicle_by_id_simple(db, vehicle_id)
        driver_id = db_vehicle.driver_id
        db_order = order_crud.change_order_driver(db, id, driver_id, vehicle_id, create_user)
        if db_order is None:
            status = 418
            error_msg = 'add_order_driver_failed'
        order_crud.add_order_history(db, id, today, models.OrderState.taken, create_user)
        if driver_id and vehicle_id:
            vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id, models.VehicleAvailable.busy)
        if old_driver_id and old_vehicle_id:
            vehicle_crud.change_vehicle_status_available(db, old_driver_id, old_vehicle_id,
                                                         models.VehicleAvailable.free)
        db.commit()
        await websocket.share_order(db, db_order, driver_id)
        await websocket.send_sms_history_driver(db, db_order, lang, "driver_changed", True)
        await websocket.check_new_order(db, old_driver_id, old_vehicle_id)
        await websocket.dashboard_vehicles(db)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        db_order = None
        error_msg = 'add_order_driver_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


async def remove_order_driver(db: Session, id, create_user, lang="ru"):
    try:
        status = 200
        error_msg = ''
        order_data = order_crud.get_order_by_id(db, id)
        old_driver_id = order_data.driver_id
        old_vehicle_id = order_data.vehicle_id
        today = datetime.now()
        db_order = order_crud.remove_order_driver(db, id, create_user)
        if db_order is None:
            status = 418
            error_msg = 'remove_order_driver_failed'
        order_crud.add_order_history(db, id, today, models.OrderState.created, create_user)
        if old_driver_id and old_vehicle_id:
            vehicle_crud.change_vehicle_status_available(db, old_driver_id, old_vehicle_id,
                                                         models.VehicleAvailable.free)
        db.commit()
        await websocket.send_sms_history_driver(db, db_order, lang, "driver_removed")
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        db_order = None
        error_msg = 'remove_order_driver_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


def change_order_state(db: Session, id, order_state, create_user):
    try:
        status = 200
        error_msg = ''
        today = datetime.now()
        db_order = order_crud.change_order_state(db, id, order_state, create_user)
        if db_order is None:
            status = 418
            error_msg = 'change_order_state_failed'
        order_crud.add_order_history(db, id, today, order_state, create_user)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        db_order = None
        error_msg = 'change_order_state_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


async def accept_order(db: Session, id, create_user, lang="ru"):
    try:
        status = 200
        error_msg = ''
        today = datetime.now()
        db_order = order_crud.accept_order(db, id, create_user)
        if db_order is None:
            status = 418
            error_msg = 'accept_order_failed'
        order_crud.add_order_history(db, id, today, models.OrderState.taken, create_user)
        db.commit()
        await websocket.dashboard_statistics(db)
        await websocket.send_sms_history(db, db_order, lang, True)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        db_order = None
        error_msg = 'accept_order_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


async def take_postponed_order(db: Session, id, driver_id, vehicle_id, create_user, lang="ru"):
    try:
        status = 200
        error_msg = ''
        db_driver = customer_crud.get_customer_balance_by_customer_minimum(db, driver_id)
        if db_driver:
            today = datetime.now()
            db_order = order_crud.take_postponed_order(db, id, driver_id, vehicle_id, create_user)
            if db_order is None:
                status = 418
                error_msg = 'take_postponed_order_failed'
            order_crud.add_order_history(db, id, today, models.OrderState.taken_post, create_user)
            db.commit()
            await websocket.dashboard_statistics(db)
            await websocket.send_sms_history(db, db_order, lang, True)
        else:
            status = 409
            db_order = None
            error_msg = 'balance_reached_minimum'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        db_order = None
        error_msg = 'take_postponed_order_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


async def accept_postponed_order(db: Session, id, create_user, lang="ru"):
    try:
        status = 200
        error_msg = ''
        today = datetime.now()
        db_order = order_crud.get_order_by_id_sample(db, id)
        driver_id = db_order.driver_id
        vehicle_id = db_order.vehicle_id
        order_id = db_order.id
        order_data = order_crud.get_order_new_by_driver(db, driver_id, vehicle_id)
        if order_data:
            if order_data.order_state == models.OrderState.started:
                status = 418
                error_msg = 'driver_has_already_started_order'
                return {"status": status, "error_msg": error_msg, "result": db_order}
            order_crud.remove_order_driver(db, order_data.id, create_user)
        db_order = order_crud.accept_order(db, id, create_user)
        if db_order is None:
            status = 418
            error_msg = 'accept_postponed_order_failed'
        order_crud.add_order_history(db, id, today, models.OrderState.taken, create_user)
        vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id, models.VehicleAvailable.busy)
        db.commit()
        await websocket.share_order(db, order_id, driver_id)
        await websocket.send_sms_history(db, db_order, lang, True)
        await websocket.check_new_order(db, driver_id, vehicle_id)
        await websocket.dashboard_statistics(db)
        await websocket.dashboard_vehicles(db)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        db_order = None
        error_msg = 'accept_postponed_order_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


async def start_order(db: Session, id, create_user, lang="ru"):
    try:
        status = 200
        error_msg = ''
        today = datetime.now()
        db_order = order_crud.change_order_state(db, id, models.OrderState.started, create_user)
        if db_order is None:
            status = 418
            error_msg = 'start_order_failed'
        order_crud.add_order_history(db, id, today, models.OrderState.started, create_user)
        db.commit()
        await websocket.send_sms_history(db, db_order, lang)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        db_order = None
        error_msg = 'start_order_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


async def finish_order(db: Session, id, pay_total, order_distance, order_time, order_wait_time, create_user, lang="ru"):
    try:
        status = 200
        error_msg = ''
        order_data = order_crud.get_order_by_id(db, id)
        driver_id = order_data.driver_id
        vehicle_id = order_data.vehicle_id
        pay_discount_prc = order_data.pay_discount_prc
        pay_discount_amount = order_data.pay_discount_amount
        current_balance = 0
        service_prc = order_data.service_prc
        today = datetime.now()
        discount = float(pay_discount_amount)
        if pay_discount_prc:
            pay_net_total = pay_total - pay_total * pay_discount_prc / 100
            discount = pay_total * pay_discount_prc / 100
        else:
            pay_net_total = pay_total - pay_discount_amount
        pay_net_total_text = num2words(int(pay_net_total), lang='ru')
        service_amount = 0
        if float(service_prc) > 0:
            service_amount = float(pay_net_total) * float(service_prc) / 100
            if discount > 0:
                discount = discount - discount * float(service_prc) / 100
        service_amount = round(service_amount, 2)
        db_order = order_crud.finish_order(db, id, pay_total, pay_net_total, pay_net_total_text, service_amount,
                                           order_distance, order_time, order_wait_time, create_user)
        if db_order is None:
            status = 418
            error_msg = 'finish_order_failed'
        order_crud.add_order_history(db, id, today, models.OrderState.finished, create_user)
        if driver_id and vehicle_id:
            vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id, models.VehicleAvailable.free)
            db_driver = customer_crud.get_customer_balance_by_customer(db, driver_id)
            current_balance = db_driver.current_balance
        if service_amount > 0:
            payment_access.add_payment(db, models.PaymentMethods.cash, driver_id, service_amount, "Заказ",
                                       None, False, create_user)
        if discount > 0:
            payment_access.add_payment(db, models.PaymentMethods.cash, driver_id, discount, "Возврат скидки",
                                       None, True, create_user)
        db.commit()
        await websocket.send_sms_history(db, db_order, lang)
        await websocket.check_new_order(db, driver_id, vehicle_id)
        await websocket.dashboard_statistics(db)
        await websocket.dashboard_vehicles(db)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        current_balance = 0
        error_msg = 'finish_order_error'
    return {"status": status, "error_msg": error_msg, "result": current_balance}


async def cancel_order(db: Session, id, create_user, lang="ru"):
    try:
        status = 200
        error_msg = ''
        order_data = order_crud.get_order_by_id(db, id)
        driver_id = order_data.driver_id
        vehicle_id = order_data.vehicle_id
        current_balance = 0
        today = datetime.now()
        db_order = order_crud.change_order_state(db, id, models.OrderState.canceled, create_user)
        if db_order is None:
            status = 418
            error_msg = 'cancel_order_failed'
        order_crud.add_order_history(db, id, today, models.OrderState.canceled, create_user)
        if driver_id and vehicle_id:
            vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id, models.VehicleAvailable.free)
            db_driver = customer_crud.get_customer_balance_by_customer(db, driver_id)
            current_balance = db_driver.current_balance
        db_customer = customer_crud.get_customer_by_id_sample(db, driver_id)
        db.commit()
        await manager.broadcast_order("", db_customer.username)
        await websocket.send_sms_history(db, db_order, lang)
        await websocket.check_new_order(db, driver_id, vehicle_id)
        await websocket.dashboard_statistics(db)
        await websocket.dashboard_vehicles(db)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        current_balance = 0
        error_msg = 'cancel_order_error'
    return {"status": status, "error_msg": error_msg, "result": current_balance}


async def reject_order(db: Session, id, district_id, create_user):
    try:
        status = 200
        error_msg = ''
        canceled_vehicles = []
        order_data = order_crud.get_order_by_id(db, id)
        driver_id = order_data.driver_id
        vehicle_id = order_data.vehicle_id
        price_cancel = order_data.price_cancel
        service_id = order_data.service_id
        district_id_from = order_data.district_id_from
        if order_data.canceled_vehicles:
            canceled_vehicles = order_data.canceled_vehicles
        canceled_vehicles.append(vehicle_id)
        if district_id is None:
            db_vehicle = vehicle_crud.get_vehicle_status_by_info(db, driver_id, vehicle_id)
            if db_vehicle:
                district_id = db_vehicle.district_id
        db_order = order_crud.reject_order(db, id, canceled_vehicles, create_user)
        if db_order is None:
            status = 418
            error_msg = 'reject_order_failed'
        if driver_id and vehicle_id:
            vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id, models.VehicleAvailable.free)
        if district_id == order_data.district_id_from:
            payment_access.add_payment(db, models.PaymentMethods.cash, driver_id, price_cancel, "За отказ заказа",
                                       None, False, create_user)
        db.commit()
        current_balance = customer_crud.get_customer_balance_by_customer(db, driver_id).current_balance
        await websocket.share_new_order(db, order_data.id, None, None, create_user, service_id, district_id_from,
                                        canceled_vehicles)
        await websocket.dashboard_statistics(db)
        await websocket.dashboard_vehicles(db)
        await websocket.check_new_order(db, driver_id, vehicle_id)
    except (IntegrityError, FlushError) as exc:
        log.exception('%s - %s', exc, create_user)
        db.rollback()
        status = 418
        current_balance = None
        error_msg = 'reject_order_error'
    return {"status": status, "error_msg": error_msg, "result": current_balance}


def get_order_by_id(db: Session, id):
    try:
        status = 200
        error_msg = ''
        db_order = order_crud.get_order_by_id(db, id)
        if db_order is None:
            status = 418
            error_msg = 'get_order_detail_by_id_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_order = None
        error_msg = 'get_order_detail_by_id_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


def search_active_by_info(db: Session, order_type, order_state, service_id, start_date, end_date, search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_order = order_crud.search_active_by_info(db, order_type, order_state, service_id, start_date, end_date,
                                                    search_text)
        if db_order is None:
            status = 418
            error_msg = 'search_active_by_info_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_order = None
        error_msg = 'search_active_by_info_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


def get_order_post_list_by_service(db: Session, driver_id, vehicle_id):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_status_by_info(db, driver_id, vehicle_id)
        db_order = order_crud.get_order_post_list_by_service(db, db_vehicle.service_ids)
        if db_order is None:
            status = 418
            error_msg = 'get_order_post_list_by_service_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_order = None
        error_msg = 'get_order_post_list_by_service_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


def get_order_post_list_by_info_service(db: Session, driver_id, vehicle_id):
    try:
        status = 200
        error_msg = ''
        db_vehicle = vehicle_crud.get_vehicle_status_by_info(db, driver_id, vehicle_id)
        db_order = order_crud.get_order_post_list_by_info_service(db, driver_id, vehicle_id, db_vehicle.service_ids)
        if db_order is None:
            status = 418
            error_msg = 'get_order_post_list_by_info_service_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_order = None
        error_msg = 'get_order_post_list_by_info_service_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


def search_active_by_driver(db: Session, driver_id, order_type, order_state, service_id, start_date, end_date,
                            search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_order = order_crud.search_active_by_driver(db, driver_id, order_type, order_state, service_id, start_date,
                                                      end_date, search_text)
        if db_order is None:
            status = 418
            error_msg = 'search_active_by_driver_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_order = None
        error_msg = 'search_active_by_driver_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


def search_active_by_client(db: Session, client_id, order_type, order_state, service_id, start_date, end_date,
                            search_text):
    try:
        status = 200
        error_msg = ''
        if not search_text:
            search_text = ''
        db_order = order_crud.search_active_by_client(db, client_id, order_type, order_state, service_id, start_date,
                                                      end_date, search_text)
        if db_order is None:
            status = 418
            error_msg = 'search_active_by_client_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_order = None
        error_msg = 'search_active_by_client_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}


# endregion


# region Order History
def get_order_history_list_by_order(db: Session, order_id):
    try:
        status = 200
        error_msg = ''
        db_order = order_crud.get_order_history_list_by_order(db, order_id)
        if db_order is None:
            status = 418
            error_msg = 'get_order_history_list_by_order_failed'
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        db_order = None
        error_msg = 'get_order_history_list_by_order_error'
    return {"status": status, "error_msg": error_msg, "result": db_order}
# endregion
