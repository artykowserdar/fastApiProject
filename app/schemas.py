from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from . import config, models


class JWTSettings(BaseModel):
    authjwt_secret_key: str = config.SECRET_KEY


class Token(BaseModel):
    access_token: str
    token_type: str
    role: models.UserRole
    username: str
    initials: Optional[dict]
    avatar_name: Optional[str]
    avatar_path: Optional[str]

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    username: Optional[str]

    class Config:
        orm_mode = True


class Users(BaseModel):
    username: Optional[str]
    role: Optional[models.UserRole]
    state: Optional[models.UserState]
    avatar_name: Optional[str]
    avatar_path: Optional[str]
    create_ts: Optional[datetime]
    update_ts: Optional[datetime]

    class Config:
        orm_mode = True


class UserInDB(Users):
    hashed_password: str

    class Config:
        orm_mode = True


class UserListView(Users):
    id: Optional[UUID]
    fullname: Optional[dict]
    initials: Optional[dict]
    address: Optional[str]
    employee_type: Optional[models.EmployeeType]

    class Config:
        orm_mode = True


class UserCustomer(Users):
    id: Optional[UUID]
    fullname: Optional[dict]
    customer_type: Optional[models.CustomerType]

    class Config:
        orm_mode = True


class UserActionLog(BaseModel):
    id: Optional[UUID]
    username: Optional[str]
    action: Optional[models.UserAction]
    sup_info: Optional[str]
    items: Optional[str]
    action_ts: Optional[datetime]

    class Config:
        orm_mode = True


class Logs(BaseModel):
    id: UUID
    action: Optional[str]
    action_user: Optional[str]
    sup_info: Optional[str]
    action_ts: Optional[datetime]

    class Config:
        orm_mode = True


class Customers(BaseModel):
    id: UUID
    code: Optional[str]
    fullname: Optional[dict]
    initials: Optional[dict]
    address: Optional[str]
    birth_date: Optional[date]
    birth_place: Optional[str]
    gender: models.GenderType
    customer_type: models.CustomerType
    discount_percent: Optional[float]
    discount_limit: Optional[float]
    phone: Optional[str]
    employee_type: Optional[models.EmployeeType]
    username: Optional[str]
    image_name: Optional[str]
    image_path: Optional[str]
    blacklist: Optional[bool]
    rating: Optional[float]
    state: models.EntityState
    create_ts: datetime
    update_ts: datetime

    class Config:
        orm_mode = True


class CustomerView(Customers):
    current_balance: Optional[float]
    employee_type: Optional[models.EmployeeType]
    username: Optional[str]

    class Config:
        orm_mode = True


class Districts(BaseModel):
    id: UUID
    district_name: Optional[dict]
    district_desc: Optional[dict]
    district_geo: Optional[list[list[float]]]
    state: models.EntityState
    create_ts: datetime
    update_ts: datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class DistrictDrivers(BaseModel):
    id: UUID
    district_name: Optional[dict]
    district_desc: Optional[dict]
    vehicles_count: Optional[int]

    class Config:
        orm_mode = True


class VehicleModels(BaseModel):
    id: UUID
    model_name: Optional[dict]
    model_desc: Optional[dict]
    state: models.EntityState
    create_ts: datetime
    update_ts: datetime

    class Config:
        orm_mode = True


class VehicleColors(BaseModel):
    id: UUID
    color_name: Optional[dict]
    color_desc: Optional[dict]
    state: models.EntityState
    create_ts: datetime
    update_ts: datetime

    class Config:
        orm_mode = True


class VehicleTypes(BaseModel):
    id: UUID
    type_name: Optional[dict]
    type_desc: Optional[dict]
    state: models.EntityState
    create_ts: datetime
    update_ts: datetime

    class Config:
        orm_mode = True


class Vehicles(BaseModel):
    id: UUID
    model_id: Optional[UUID]
    type_id: Optional[UUID]
    vehicle_name: Optional[dict]
    document_no: Optional[str]
    vehicle_no: Optional[str]
    vehicle_year: Optional[int]
    vehicle_color: Optional[dict]
    engine_no: Optional[str]
    body_no: Optional[str]
    max_weight: Optional[str]
    net_weight: Optional[str]
    validity: Optional[str]
    vehicle_desc: Optional[str]
    driver_id: Optional[UUID]
    state: models.EntityState
    create_ts: datetime
    update_ts: datetime

    class Config:
        orm_mode = True


class VehicleView(Vehicles):
    model_name: Optional[dict]
    type_name: Optional[dict]
    fullname: Optional[dict]
    color_id: Optional[UUID]
    vehicle_available: Optional[models.VehicleAvailable]
    vehicle_state: Optional[models.VehicleState]
    district_name: Optional[dict]

    class Config:
        orm_mode = True


class Shifts(BaseModel):
    id: UUID
    shift_name: str
    shift_desc: Optional[str]
    shift_start_time: datetime
    shift_end_time: datetime
    state: models.EntityState
    create_ts: datetime
    update_ts: datetime

    class Config:
        orm_mode = True


class ShiftVehicles(BaseModel):
    id: UUID
    shift_id: UUID
    vehicle_id: UUID
    state: models.EntityState
    create_ts: datetime
    update_ts: datetime

    class Config:
        orm_mode = True


class ShiftVehicleView(ShiftVehicles):
    shift_name: str
    shift_desc: Optional[str]
    shift_start_time: datetime
    shift_end_time: datetime
    vehicle_name: Optional[dict]
    type_name: Optional[dict]
    fullname: Optional[dict]
    vehicle_state : Optional[bool]

    class Config:
        orm_mode = True


class Services(BaseModel):
    id: UUID
    service_name: Optional[dict]
    service_desc: Optional[dict]
    service_priority: Optional[int]
    state: models.EntityState
    create_ts: datetime
    update_ts: datetime

    class Config:
        orm_mode = True


class ServiceVehicles(BaseModel):
    id: UUID
    service_id: UUID
    vehicle_id: UUID
    state: models.EntityState
    create_ts: datetime
    update_ts: datetime

    class Config:
        orm_mode = True


class ServiceVehicleView(ServiceVehicles):
    service_name: Optional[dict]
    service_desc: Optional[dict]
    vehicle_name: Optional[dict]
    type_name: Optional[dict]
    fullname: Optional[dict]

    class Config:
        orm_mode = True


class Rates(BaseModel):
    id: UUID
    rate_name: Optional[str]
    rate_desc: Optional[str]
    service_id: Optional[UUID]
    shift_id: Optional[UUID]
    district_ids: Optional[List[UUID]]
    district_names: Optional[List[dict]]
    start_date: Optional[date]
    end_date: Optional[date]
    price_km: Optional[float]
    price_min: Optional[float]
    price_wait_min: Optional[float]
    minute_free_wait: Optional[float]
    km_free: Optional[float]
    price_delivery: Optional[float]
    minute_for_wait: Optional[float]
    price_cancel: Optional[float]
    price_minimal: Optional[float]
    service_prc: Optional[float]
    birthday_discount_prc: Optional[float]
    state: models.EntityState
    create_ts: datetime
    update_ts: datetime

    class Config:
        orm_mode = True


class RateView(Rates):
    service_name: Optional[dict]
    service_desc: Optional[dict]
    shift_name: Optional[str]
    shift_desc: Optional[str]
    shift_start_time: datetime
    shift_end_time: datetime

    class Config:
        orm_mode = True


class RateView2(BaseModel):
    rate_id: UUID
    service_id: Optional[UUID]
    shift_id: Optional[UUID]
    start_date: Optional[date]
    end_date: Optional[date]
    price_km: Optional[float]
    price_min: Optional[float]
    price_wait_min: Optional[float]
    minute_free_wait: Optional[float]
    km_free: Optional[float]
    price_delivery: Optional[float]
    minute_for_wait: Optional[float]
    price_cancel: Optional[float]
    price_minimal: Optional[float]
    service_prc: Optional[float]
    birthday_discount_prc: Optional[float]
    service_name: Optional[dict]
    shift_name: Optional[str]
    order_price: Optional[float]

    class Config:
        orm_mode = True


class SearchAddress(BaseModel):
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    district_id: Optional[UUID]

    class Config:
        orm_mode = True


class Orders(BaseModel):
    id: Optional[UUID]
    driver_id: Optional[UUID]
    vehicle_id: Optional[UUID]
    client_id: Optional[UUID]
    service_id: Optional[UUID]
    shift_id: Optional[UUID]
    rate_id: Optional[UUID]
    district_id_from: Optional[UUID]
    district_id_to: Optional[UUID]
    order_address_from: Optional[dict]
    order_address_to: Optional[dict]
    order_code: Optional[str]
    order_desc: Optional[str]
    order_date: Optional[datetime]
    order_type: Optional[models.OrderType]
    order_state: Optional[models.OrderState]
    pay_total: Optional[float]
    pay_discount_prc: Optional[float]
    pay_discount_amount: Optional[float]
    pay_net_total: Optional[float]
    pay_net_total_text: Optional[str]
    service_prc: Optional[float]
    service_amount: Optional[float]
    order_distance: Optional[float]
    order_time: Optional[float]
    order_wait_time: Optional[float]
    order_user: Optional[str]
    create_user: Optional[str]
    state: Optional[models.EntityState]
    create_ts: Optional[datetime]
    update_ts: Optional[datetime]

    class Config:
        orm_mode = True


class OrderView(Orders):
    fullname: Optional[dict]
    discount_percent: Optional[float]
    discount_limit: Optional[float]
    phone: Optional[str]
    driver_fullname: Optional[dict]
    service_name: Optional[dict]
    shift_name: Optional[str]
    vehicle_name: Optional[dict]
    price_km: Optional[float]
    price_min: Optional[float]
    price_wait_min: Optional[float]
    minute_free_wait: Optional[float]
    km_free: Optional[float]
    price_delivery: Optional[float]
    minute_for_wait: Optional[float]
    price_cancel: Optional[float]
    price_minimal: Optional[float]

    class Config:
        orm_mode = True


class Payments(BaseModel):
    id: Optional[UUID]
    payment_method: Optional[models.PaymentMethods]
    customer_id: Optional[UUID]
    payment_code: Optional[str]
    payment_amount: Optional[float]
    payment_amount_text: Optional[dict]
    payment_date: Optional[datetime]
    payment_desc: Optional[str]
    in_out: Optional[bool]
    create_user: Optional[str]
    state: Optional[models.EntityState]
    create_ts: Optional[datetime]
    update_ts: Optional[datetime]

    class Config:
        orm_mode = True


class PaymentView(Payments):
    fullname: Optional[dict]
    phone: Optional[str]

    class Config:
        orm_mode = True


class OrderHistory(BaseModel):
    id: Optional[UUID]
    order_id: Optional[UUID]
    order_date: Optional[datetime]
    order_state: Optional[models.OrderState]
    action_user: Optional[str]
    create_ts: Optional[datetime]

    class Config:
        orm_mode = True


class OrderHistoryView(OrderHistory):
    fullname: Optional[dict]

    class Config:
        orm_mode = True


class DashboardStatistics(BaseModel):
    standart_orders: Optional[int]
    standart_orders_1: Optional[int]
    postponed_orders: Optional[int]
    postponed_orders_1: Optional[int]
    waiting_orders: Optional[int]
    active_vehicles: Optional[int]
    free_vehicles: Optional[int]

    class Config:
        orm_mode = True


class DashboardVehicles(BaseModel):
    driver_id: Optional[str]
    vehicle_id: Optional[str]
    geo_location: Optional[List[float]]
    vehicle_available: Optional[str]
    vehicle_name: Optional[dict]
    fullname: Optional[dict]

    class Config:
        orm_mode = True


class ClientAddressHistory(BaseModel):
    id: Optional[UUID]
    client_id: Optional[UUID]
    district_id: Optional[UUID]
    address_type: Optional[models.AddressType]
    address: Optional[str]
    coordinates: Optional[str]
    state: Optional[models.EntityState]
    create_ts: Optional[datetime]
    update_ts: Optional[datetime]

    class Config:
        orm_mode = True


class CustomerRatings(BaseModel):
    id: Optional[UUID]
    set_customer_id: Optional[UUID]
    get_customer_id: Optional[UUID]
    rating: Optional[int]
    comment: Optional[str]
    state: Optional[models.EntityState]
    create_ts: Optional[datetime]
    update_ts: Optional[datetime]

    class Config:
        orm_mode = True


class CustomerRatingView(CustomerRatings):
    fullname: Optional[dict]

    class Config:
        orm_mode = True
