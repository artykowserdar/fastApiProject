import logging
from uuid import UUID

from geoalchemy2.shape import to_shape
from shapely import wkt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app import models, schemas
from app.accesses import token_access, temp_access, vehicle_access, geo_access
from app.cruds import customer_crud, vehicle_crud, order_crud
from app.database import get_db
from app.lib import get_remote_ip
from app.websocket.manager import ConnectionManager

router = APIRouter()
log = logging.getLogger(__name__)

manager = ConnectionManager()


async def share_new_order(db: Session, order_id, vehicle_id, driver_id, create_user, service_id, district_id_from,
                          canceled_vehicles):
    fullname = None
    username = None
    order_personal = False
    order_data = order_crud.get_order_by_id(db, order_id)
    order_type = order_data.order_type
    order_id = order_data.id
    if driver_id is None:
        db_vehicle = vehicle_crud.get_vehicle_status_free_by_district(db, service_id, district_id_from,
                                                                      canceled_vehicles)
        if db_vehicle:
            driver_id = db_vehicle.driver_id
            vehicle_id = db_vehicle.vehicle_id
            fullname = db_vehicle.fullname
            username = db_vehicle.username
        else:
            db_vehicle = vehicle_crud.get_vehicle_status_free(db, service_id, canceled_vehicles)
            if db_vehicle:
                driver_id = db_vehicle.driver_id
                vehicle_id = db_vehicle.vehicle_id
                fullname = db_vehicle.fullname
                username = db_vehicle.username
    else:
        db_driver = customer_crud.get_customer_by_id_sample(db, driver_id)
        username = db_driver.username
        order_personal = True
    order_data = {
        "id": str(order_data.id),
        "order_date": str(order_data.order_date),
        "order_address_to": order_data.order_address_to["address"],
        "order_address_from": order_data.order_address_from["address"],
        "order_coordinates_to": order_data.order_address_to["coordinates"],
        "order_coordinates_from": order_data.order_address_from["coordinates"],
        "order_state": order_data.order_state.name,
        "order_type": order_data.order_type.name,
        "order_desc": order_data.order_desc,
        "service_name": order_data.service_name,
        "pay_discount_prc": order_data.pay_discount_prc,
        "price_km": order_data.price_km,
        "price_min": order_data.price_min,
        "price_wait_min": order_data.price_wait_min,
        "minute_free_wait": order_data.minute_free_wait,
        "km_free": order_data.km_free,
        "price_delivery": order_data.price_delivery,
        "minute_for_wait": order_data.minute_for_wait,
        "price_cancel": order_data.price_cancel,
        "price_minimal": order_data.price_minimal,
        "phone": order_data.phone,
        "fullname": fullname,
        "json_type": "new_order"
    }
    if order_personal:
        await manager.broadcast_order(order_data, username)
        order_crud.add_order_driver(db, order_id, driver_id, vehicle_id, create_user)
        db_vehicle_state = vehicle_crud.get_vehicle_status_free_simple(db, driver_id, vehicle_id)
        if db_vehicle_state:
            vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id, models.VehicleAvailable.busy)
        db.commit()
    else:
        if order_type == models.OrderType.standart:
            result = await manager.broadcast_order(order_data, username)
            if result:
                order_crud.add_order_driver(db, order_id, driver_id, vehicle_id, create_user)
                vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id, models.VehicleAvailable.busy)
                db.commit()
            else:
                await share_new_order2(db, order_id, order_data, create_user, service_id, district_id_from,
                                       canceled_vehicles)
        else:
            db_customer = customer_crud.get_customer_active_list_employee_driver(db)
            for customer in db_customer:
                if customer.username:
                    await manager.broadcast_order(order_data, customer.username)
    return True


async def share_new_order2(db: Session, order_id, order_data, create_user, service_id, district_id_from,
                           canceled_vehicles):
    driver_id = None
    vehicle_id = None
    username = None
    db_vehicle = vehicle_crud.get_vehicle_status_free_by_district(db, service_id, district_id_from, canceled_vehicles)
    if db_vehicle:
        driver_id = db_vehicle.driver_id
        vehicle_id = db_vehicle.vehicle_id
        username = db_vehicle.username
    else:
        db_vehicle = vehicle_crud.get_vehicle_status_free(db, service_id, canceled_vehicles)
        if db_vehicle:
            driver_id = db_vehicle.driver_id
            vehicle_id = db_vehicle.vehicle_id
            username = db_vehicle.username
    if driver_id:
        result = await manager.broadcast_order(order_data, username)
        if result:
            order_crud.add_order_driver(db, order_id, driver_id, vehicle_id, create_user)
            vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id, models.VehicleAvailable.busy)
            db.commit()
        else:
            await share_new_order2(db, order_id, order_data, create_user, service_id, district_id_from,
                                   canceled_vehicles)
    return True


async def share_order(db: Session, order_id, driver_id):
    db_driver = customer_crud.get_customer_by_id_sample(db, driver_id)
    fullname = db_driver.fullname
    username = db_driver.username
    db_order = order_crud.get_order_by_id(db, order_id)
    order_data = {
        "id": str(db_order.id),
        "order_date": str(db_order.order_date),
        "order_address_to": db_order.order_address_to["address"],
        "order_address_from": db_order.order_address_from["address"],
        "order_coordinates_to": db_order.order_address_to["coordinates"],
        "order_coordinates_from": db_order.order_address_from["coordinates"],
        "order_state": db_order.order_state.name,
        "order_type": db_order.order_type.name,
        "order_desc": db_order.order_desc,
        "service_name": db_order.service_name,
        "pay_discount_prc": db_order.pay_discount_prc,
        "price_km": db_order.price_km,
        "price_min": db_order.price_min,
        "price_wait_min": db_order.price_wait_min,
        "minute_free_wait": db_order.minute_free_wait,
        "km_free": db_order.km_free,
        "price_delivery": db_order.price_delivery,
        "minute_for_wait": db_order.minute_for_wait,
        "price_cancel": db_order.price_cancel,
        "price_minimal": db_order.price_minimal,
        "phone": db_order.phone,
        "fullname": fullname,
        "json_type": "new_order"
    }

    await manager.broadcast_order(order_data, username)
    return True


async def send_sms(db: Session, order_data, lang):
    db_customer = customer_crud.get_customer_by_id_sample(db, order_data.client_id)
    order_data = {
        # "order_date": str(order_data.order_date.strftime("%d.%m.%Y %H:%M")),
        # "order_address_to": order_data.order_address_to["address"],
        # "order_address_from": order_data.order_address_from["address"],
        "vehicle_name": "",
        "order_state": order_data.order_state.name,
        "time": 0,
        "phone": db_customer.phone,
        "lang": lang,
        "pay_net_total": order_data.pay_net_total,
        "json_type": "new_order"
    }
    await manager.broadcast_order(order_data, "sms")
    return True


async def send_sms_history(db: Session, order_id, lang, time=False):
    order_data = order_crud.get_order_by_id(db, order_id)
    time_left = 0
    if time:
        db_driver = vehicle_crud.get_driver_vehicle_location_last_by_info(db, order_data.driver_id,
                                                                          order_data.vehicle_id)
        geo_location = db_driver.geo_location
        shapely_geometry = to_shape(geo_location)
        wkt_representation = shapely_geometry.wkt
        point = wkt.loads(wkt_representation)
        coordinates = list(point.coords[0])
        db_geo = geo_access.get_distance_between_coordinates_full2(coordinates,
                                                                   order_data.order_address_from["coordinates"])
        if db_geo:
            time_left = db_geo["time"]
    db_customer = customer_crud.get_customer_by_id_sample(db, order_data.client_id)
    vehicle_name = ""
    if order_data.vehicle_name:
        vehicle_name = order_data.vehicle_name[lang]
    order_data = {
        "vehicle_name": vehicle_name,
        "order_state": order_data.order_state.name,
        "time": time_left,
        "phone": db_customer.phone,
        "lang": lang,
        "pay_net_total": order_data.pay_net_total,
        "json_type": "new_order"
    }
    await manager.broadcast_order(order_data, "sms")
    return True


async def send_sms_history_driver(db: Session, order_id, lang, order_state, time=False):
    order_data = order_crud.get_order_by_id(db, order_id)
    time_left = 0
    if time:
        db_driver = vehicle_crud.get_driver_vehicle_location_last_by_info(db, order_data.driver_id,
                                                                          order_data.vehicle_id)
        geo_location = db_driver.geo_location
        shapely_geometry = to_shape(geo_location)
        wkt_representation = shapely_geometry.wkt
        point = wkt.loads(wkt_representation)
        coordinates = list(point.coords[0])
        db_geo = geo_access.get_distance_between_coordinates_full2(coordinates,
                                                                   order_data.order_address_from["coordinates"])
        if db_geo:
            time_left = db_geo["time"]
    db_customer = customer_crud.get_customer_by_id_sample(db, order_data.client_id)
    vehicle_name = ""
    if order_data.vehicle_name:
        vehicle_name = order_data.vehicle_name[lang]
    order_data = {
        "vehicle_name": vehicle_name,
        "order_state": order_state,
        "time": time_left,
        "phone": db_customer.phone,
        "lang": lang,
        "pay_net_total": order_data.pay_net_total,
        "json_type": "new_order"
    }
    await manager.broadcast_order(order_data, "sms")
    return True


async def new_user_sms(phone, lang, phone_code):
    password = temp_access.create_user_password()
    order_data = {
        "password": password,
        "phone": phone,
        "phone_code": phone_code,
        "lang": lang,
        "json_type": "new_user"
    }
    await manager.broadcast_order(order_data, "sms")
    return password


async def dashboard_statistics(db: Session):
    json_data = temp_access.dashboard_statistics(db)["result"]
    db_customer = customer_crud.get_customer_active_list_employee_boss(db)
    for customer in db_customer:
        if customer.username:
            await manager.broadcast_order(json_data, customer.username)
    return True


async def dashboard_vehicles(db: Session):
    json_data = vehicle_access.get_vehicle_status_active_list_dashboard(db)["result"]
    db_customer = customer_crud.get_customer_active_list_employee_boss(db)
    for customer in db_customer:
        if customer.username:
            await manager.broadcast_order(json_data, customer.username)
    return True


@router.get("/check-new-order-of-driver/{driver_id}/{vehicle_id}/")
async def check_new_order_by_driver(request: Request, driver_id: UUID, vehicle_id: UUID, db: Session = Depends(get_db),
                                    current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                    authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Check new order of driver - %s", current_user.username, get_remote_ip(request))

    db_vehicle = vehicle_crud.get_vehicle_status_by_info_minimum(db, driver_id, vehicle_id)
    order_data = order_crud.get_order_new_by_driver(db, driver_id, vehicle_id)
    if order_data:
        db_customer = customer_crud.get_customer_by_id_sample(db, driver_id)
        vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id, models.VehicleAvailable.busy)
        order_data = {
            "id": str(order_data.id),
            "order_date": str(order_data.order_date),
            "order_address_to": order_data.order_address_to["address"],
            "order_address_from": order_data.order_address_from["address"],
            "order_coordinates_to": order_data.order_address_to["coordinates"],
            "order_coordinates_from": order_data.order_address_from["coordinates"],
            "order_state": order_data.order_state.name,
            "order_type": order_data.order_type.name,
            "order_desc": order_data.order_desc,
            "service_name": order_data.service_name,
            "pay_discount_prc": order_data.pay_discount_prc,
            "price_km": order_data.price_km,
            "price_min": order_data.price_min,
            "price_wait_min": order_data.price_wait_min,
            "minute_free_wait": order_data.minute_free_wait,
            "km_free": order_data.km_free,
            "price_delivery": order_data.price_delivery,
            "minute_for_wait": order_data.minute_for_wait,
            "price_cancel": order_data.price_cancel,
            "price_minimal": order_data.price_minimal,
            "phone": order_data.phone,
            "fullname": db_customer.fullname,
            "json_type": "new_order"
        }
        await manager.broadcast_order(order_data, db_customer.username)
    else:
        if db_vehicle:
            order_data = order_crud.get_order_new_by_info(db, db_vehicle.service_ids, db_vehicle.district_id,
                                                          vehicle_id)
            if order_data:
                order_id = order_data.id
                db_customer = customer_crud.get_customer_by_id_sample(db, driver_id)
                vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id, models.VehicleAvailable.busy)
                order_data = {
                    "id": str(order_id),
                    "order_date": str(order_data.order_date),
                    "order_address_to": order_data.order_address_to["address"],
                    "order_address_from": order_data.order_address_from["address"],
                    "order_coordinates_to": order_data.order_address_to["coordinates"],
                    "order_coordinates_from": order_data.order_address_from["coordinates"],
                    "order_state": order_data.order_state.name,
                    "order_type": order_data.order_type.name,
                    "order_desc": order_data.order_desc,
                    "service_name": order_data.service_name,
                    "pay_discount_prc": order_data.pay_discount_prc,
                    "price_km": order_data.price_km,
                    "price_min": order_data.price_min,
                    "price_wait_min": order_data.price_wait_min,
                    "minute_free_wait": order_data.minute_free_wait,
                    "km_free": order_data.km_free,
                    "price_delivery": order_data.price_delivery,
                    "minute_for_wait": order_data.minute_for_wait,
                    "price_cancel": order_data.price_cancel,
                    "price_minimal": order_data.price_minimal,
                    "phone": order_data.phone,
                    "fullname": db_customer.fullname,
                    "json_type": "new_order"
                }
                await manager.broadcast_order(order_data, db_customer.username)
                order_crud.add_order_driver(db, order_id, driver_id, vehicle_id, db_customer.username)
                vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id, models.VehicleAvailable.busy)
            else:
                order_data = order_crud.get_order_new_by_service(db, db_vehicle.service_ids, vehicle_id)
                if order_data:
                    order_id = order_data.id
                    db_customer = customer_crud.get_customer_by_id_sample(db, driver_id)
                    vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id,
                                                                 models.VehicleAvailable.busy)
                    order_data = {
                        "id": str(order_id),
                        "order_date": str(order_data.order_date),
                        "order_address_to": order_data.order_address_to["address"],
                        "order_address_from": order_data.order_address_from["address"],
                        "order_coordinates_to": order_data.order_address_to["coordinates"],
                        "order_coordinates_from": order_data.order_address_from["coordinates"],
                        "order_state": order_data.order_state.name,
                        "order_type": order_data.order_type.name,
                        "order_desc": order_data.order_desc,
                        "service_name": order_data.service_name,
                        "pay_discount_prc": order_data.pay_discount_prc,
                        "price_km": order_data.price_km,
                        "price_min": order_data.price_min,
                        "price_wait_min": order_data.price_wait_min,
                        "minute_free_wait": order_data.minute_free_wait,
                        "km_free": order_data.km_free,
                        "price_delivery": order_data.price_delivery,
                        "minute_for_wait": order_data.minute_for_wait,
                        "price_cancel": order_data.price_cancel,
                        "price_minimal": order_data.price_minimal,
                        "phone": order_data.phone,
                        "fullname": db_customer.fullname,
                        "json_type": "new_order"
                    }
                    await manager.broadcast_order(order_data, db_customer.username)
                    order_crud.add_order_driver(db, order_id, driver_id, vehicle_id, db_customer.username)
                    vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id,
                                                                 models.VehicleAvailable.busy)
            db.commit()

    return None


async def check_new_order(db: Session, driver_id, vehicle_id):
    if driver_id and vehicle_id:
        db_vehicle = vehicle_crud.get_vehicle_status_by_info_minimum(db, driver_id, vehicle_id)
        db_customer = customer_crud.get_customer_by_id_sample(db, driver_id)
        order_data = order_crud.get_order_new_by_driver(db, driver_id, vehicle_id)
        if order_data:
            vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id, models.VehicleAvailable.busy)
            order_data = {
                "id": str(order_data.id),
                "order_date": str(order_data.order_date),
                "order_address_to": order_data.order_address_to["address"],
                "order_address_from": order_data.order_address_from["address"],
                "order_coordinates_to": order_data.order_address_to["coordinates"],
                "order_coordinates_from": order_data.order_address_from["coordinates"],
                "order_state": order_data.order_state.name,
                "order_type": order_data.order_type.name,
                "order_desc": order_data.order_desc,
                "service_name": order_data.service_name,
                "pay_discount_prc": order_data.pay_discount_prc,
                "price_km": order_data.price_km,
                "price_min": order_data.price_min,
                "price_wait_min": order_data.price_wait_min,
                "minute_free_wait": order_data.minute_free_wait,
                "km_free": order_data.km_free,
                "price_delivery": order_data.price_delivery,
                "minute_for_wait": order_data.minute_for_wait,
                "price_cancel": order_data.price_cancel,
                "price_minimal": order_data.price_minimal,
                "phone": order_data.phone,
                "fullname": db_customer.fullname,
                "json_type": "new_order"
            }
            await manager.broadcast_order(order_data, db_customer.username)
        else:
            if db_vehicle:
                order_data = order_crud.get_order_new_by_info(db, db_vehicle.service_ids, db_vehicle.district_id,
                                                              vehicle_id)
                if order_data:
                    order_id = order_data.id
                    vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id,
                                                                 models.VehicleAvailable.busy)
                    order_data = {
                        "id": str(order_id),
                        "order_date": str(order_data.order_date),
                        "order_address_to": order_data.order_address_to["address"],
                        "order_address_from": order_data.order_address_from["address"],
                        "order_coordinates_to": order_data.order_address_to["coordinates"],
                        "order_coordinates_from": order_data.order_address_from["coordinates"],
                        "order_state": order_data.order_state.name,
                        "order_type": order_data.order_type.name,
                        "order_desc": order_data.order_desc,
                        "service_name": order_data.service_name,
                        "pay_discount_prc": order_data.pay_discount_prc,
                        "price_km": order_data.price_km,
                        "price_min": order_data.price_min,
                        "price_wait_min": order_data.price_wait_min,
                        "minute_free_wait": order_data.minute_free_wait,
                        "km_free": order_data.km_free,
                        "price_delivery": order_data.price_delivery,
                        "minute_for_wait": order_data.minute_for_wait,
                        "price_cancel": order_data.price_cancel,
                        "price_minimal": order_data.price_minimal,
                        "phone": order_data.phone,
                        "fullname": db_customer.fullname,
                        "json_type": "new_order"
                    }
                    await manager.broadcast_order(order_data, db_customer.username)
                    order_crud.add_order_driver(db, order_id, driver_id, vehicle_id, db_customer.username)
                    vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id,
                                                                 models.VehicleAvailable.busy)
                else:
                    order_data = order_crud.get_order_new_by_service(db, db_vehicle.service_ids, vehicle_id)
                    if order_data:
                        order_id = order_data.id
                        vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id,
                                                                     models.VehicleAvailable.busy)
                        order_data = {
                            "id": str(order_id),
                            "order_date": str(order_data.order_date),
                            "order_address_to": order_data.order_address_to["address"],
                            "order_address_from": order_data.order_address_from["address"],
                            "order_coordinates_to": order_data.order_address_to["coordinates"],
                            "order_coordinates_from": order_data.order_address_from["coordinates"],
                            "order_state": order_data.order_state.name,
                            "order_type": order_data.order_type.name,
                            "order_desc": order_data.order_desc,
                            "service_name": order_data.service_name,
                            "pay_discount_prc": order_data.pay_discount_prc,
                            "price_km": order_data.price_km,
                            "price_min": order_data.price_min,
                            "price_wait_min": order_data.price_wait_min,
                            "minute_free_wait": order_data.minute_free_wait,
                            "km_free": order_data.km_free,
                            "price_delivery": order_data.price_delivery,
                            "minute_for_wait": order_data.minute_for_wait,
                            "price_cancel": order_data.price_cancel,
                            "price_minimal": order_data.price_minimal,
                            "phone": order_data.phone,
                            "fullname": db_customer.fullname,
                            "json_type": "new_order"
                        }
                        await manager.broadcast_order(order_data, db_customer.username)
                        order_crud.add_order_driver(db, order_id, driver_id, vehicle_id, db_customer.username)
                        vehicle_crud.change_vehicle_status_available(db, driver_id, vehicle_id,
                                                                     models.VehicleAvailable.busy)
                db.commit()

    return None


@router.websocket("/new-orders/{username}/")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket, username)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, username)
