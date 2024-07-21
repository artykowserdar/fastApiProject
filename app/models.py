import enum

from geoalchemy2 import Geometry
from sqlalchemy import (Column, DateTime, Enum, ForeignKey, String, Text, Float, Boolean, Integer, Date)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import select

from .database import Base
from .util.sqlalchemy import GUID


# region Enums
class UserRole(enum.Enum):
    system = 'Система'
    admin = 'Администратор'
    user = 'Пользователь'


class UserState(enum.Enum):
    enabled = 'Включен'
    disabled = 'Выключен'
    deleted = 'Удален'


class EntityState(enum.Enum):
    active = 'Активный'
    deleted = 'Удален'


class EmployeeType(enum.Enum):
    admin = 'Админ'
    boss = 'Начальник'
    operator = 'Оператор'
    driver = 'Водитель'


class CustomerType(enum.Enum):
    employee = 'Сотрудник'
    client = 'Клиент'


class GenderType(enum.Enum):
    man = 'Мужской'
    woman = 'Женский'


class VehicleAvailable(enum.Enum):
    free = 'Свободен'
    busy = 'Занят'


class VehicleState(enum.Enum):
    active = 'Активный'
    disable = 'Неактивный'


class OrderType(enum.Enum):
    standart = 'Стандарт'
    postponed = 'Отложенные'


class OrderState(enum.Enum):
    created = 'Новый'
    taken_post = 'Взятый Предзаказ'
    taken = 'Взятый'
    started = 'Начат'
    finished = 'Завершенный'
    canceled = 'Отмененный'


class AddressType(enum.Enum):
    address_from = 'Откуда'
    address_to = 'Куда'


class PaymentMethods(enum.Enum):
    cash = 'Наличные'
    pos = 'Платежный терминал'
    bank = 'Банковский перевод'
    online = 'Онлайн платеж'
    other = 'Другой способ оплаты'


# endregion


# region Action Enums
class UserAction(enum.Enum):
    UserLogIn = 'user.login'
    UserCreate = 'user.create'
    UserEdit = 'user.create'
    UserChangePassword = 'user.pwd-change'
    UserRoleChange = 'user.role-change'
    UserStateChange = 'user.state-change'
    UserLogOut = 'user.logout'
    UserCashRegisterOpen = 'user.cash-register-open'


class CustomerAction(enum.Enum):
    CustomerAdd = 'customer.add'
    CustomerAddBlacklist = 'customer.add-blacklist'
    CustomerEdit = 'customer.edit'
    CustomerStateChange = 'customer.state-change'


class EmployeeAction(enum.Enum):
    EmployeeAdd = 'employee.add'
    EmployeeEdit = 'employee.edit'
    EmployeeEditUsername = 'employee.edit-username'


class CustomerBalanceAction(enum.Enum):
    CustomerBalanceAdd = 'customer-balance.add'
    CustomerBalanceEdit = 'customer-balance.edit'
    CustomerBalanceStateChange = 'customer-balance.state-change'


class VehicleModelAction(enum.Enum):
    VehicleModelAdd = 'vehicle-model.add'
    VehicleModelEdit = 'vehicle-model.edit'
    VehicleModelStateChange = 'vehicle-model.state-change'


class VehicleColorAction(enum.Enum):
    VehicleColorAdd = 'vehicle-color.add'
    VehicleColorEdit = 'vehicle-color.edit'
    VehicleColorStateChange = 'vehicle-color.state-change'


class VehicleTypeAction(enum.Enum):
    VehicleTypeAdd = 'vehicle-type.add'
    VehicleTypeEdit = 'vehicle-type.edit'
    VehicleTypeStateChange = 'vehicle-type.state-change'


class VehicleAction(enum.Enum):
    VehicleAdd = 'vehicle.add'
    VehicleEdit = 'vehicle.edit'
    VehicleStateChange = 'vehicle.state-change'


class ShiftAction(enum.Enum):
    ShiftAdd = 'shift.add'
    ShiftEdit = 'shift.edit'
    ShiftStateChange = 'shift.state-change'


class ShiftVehicleAction(enum.Enum):
    ShiftVehicleAdd = 'shift-vehicle.add'
    ShiftVehicleStateChange = 'shift-vehicle.state-change'


class ServiceAction(enum.Enum):
    ServiceAdd = 'service.add'
    ServiceEdit = 'service.edit'
    ServiceStateChange = 'service.state-change'


class ServiceVehicleAction(enum.Enum):
    ServiceVehicleAdd = 'service-vehicle.add'
    ServiceVehicleStateChange = 'service-vehicle.state-change'


class RateAction(enum.Enum):
    RateAdd = 'rate.add'
    RateEdit = 'rate.edit'
    RateStateChange = 'rate.state-change'


class DistrictAction(enum.Enum):
    DistrictAdd = 'district.add'
    DistrictEdit = 'district.edit'
    DistrictStateChange = 'district.state-change'


class OrderAction(enum.Enum):
    OrderAdd = 'order.add'
    OrderEdit = 'order.edit'
    OrderDriverRemove = 'order.remove-order-driver'
    OrderDriverChange = 'order.change-order-driver'
    OrderStateChange = 'order.state-change'


class SettingAction(enum.Enum):
    SettingAdd = 'setting.add'
    SettingEdit = 'setting.edit'


class PaymentAction(enum.Enum):
    PaymentAdd = 'payment.add'
    PaymentEdit = 'payment.edit'
    PaymentEditPayment = 'payment.edit-payment'
    PaymentStateChange = 'payment.state-change'


# endregion


# region Models
class Users(Base):
    __tablename__ = "tbl_user"
    username = Column(String(256), primary_key=True, index=True)
    hashed_password = Column(String(256), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    state = Column(Enum(UserState), nullable=False)
    avatar_name = Column(String(64), nullable=True)
    avatar_path = Column(Text(), nullable=True)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class UserLog(Base):
    __tablename__ = 'tbl_user_log'
    id = Column(GUID, primary_key=True, index=True)
    username = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    action = Column(Enum(UserAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class UserActionLog(Base):
    __tablename__ = 'tbl_user_action_log'
    id = Column(GUID, primary_key=True, index=True)
    username = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False, index=True)
    action = Column(Enum(UserAction), nullable=False)
    sup_info = Column(Text(), nullable=True)
    items = Column(Text(), nullable=True)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class Customers(Base):
    __tablename__ = "tbl_customer"
    id = Column(GUID, primary_key=True, index=True)
    code = Column(String(32), nullable=False, unique=True, index=True)
    fullname = Column(String(256), nullable=False, index=True)
    initials = Column(String(256), nullable=True, index=True)
    address = Column(String(256), nullable=True)
    birth_date = Column(Date(), nullable=True)
    birth_place = Column(String(256), nullable=True)
    gender = Column(Enum(GenderType), nullable=False)
    customer_type = Column(Enum(CustomerType), nullable=False)
    discount_percent = Column(Float(), nullable=True, default=0)
    discount_limit = Column(Float(), nullable=True, default=0)
    card_no = Column(String(256), nullable=True, index=True)
    phone = Column(String(16), nullable=True, index=True)
    employee_type = Column(Enum(EmployeeType), nullable=True)
    username = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=True, index=True)
    image_name = Column(String(64), nullable=True)
    image_path = Column(Text(), nullable=True)
    blacklist = Column(Boolean(), nullable=False, default=False)
    rating = Column(Float(), nullable=False, default=0)
    search_meta = Column(ARRAY(Text), nullable=True, index=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class CustomerLog(Base):
    __tablename__ = 'tbl_customer_log'
    id = Column(GUID, primary_key=True, index=True)
    customer_id = Column(GUID, ForeignKey(Customers.id, deferrable=True), nullable=False)
    action = Column(Enum(CustomerAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class CustomerBalances(Base):
    __tablename__ = 'tbl_customer_balance'
    id = Column(GUID, primary_key=True, index=True)
    customer_id = Column(GUID, ForeignKey(Customers.id, deferrable=True), nullable=False, index=True)
    current_balance = Column(Float(), nullable=False)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class CustomerBalanceLog(Base):
    __tablename__ = 'tbl_customer_balance_log'
    id = Column(GUID, primary_key=True, index=True)
    customer_balance_id = Column(GUID, ForeignKey(CustomerBalances.id, deferrable=True), nullable=False, index=True)
    action = Column(Enum(CustomerBalanceAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class VehicleModels(Base):
    __tablename__ = 'tbl_vehicle_model'
    id = Column(GUID, primary_key=True, index=True)
    model_name = Column(String(256), nullable=False)
    model_desc = Column(String(256), nullable=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class VehicleModelLog(Base):
    __tablename__ = 'tbl_vehicle_model_log'
    id = Column(GUID, primary_key=True, index=True)
    vehicle_model_id = Column(GUID, ForeignKey(VehicleModels.id, deferrable=True), nullable=False, index=True)
    action = Column(Enum(VehicleModelAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class VehicleColors(Base):
    __tablename__ = 'tbl_vehicle_color'
    id = Column(GUID, primary_key=True, index=True)
    color_name = Column(String(256), nullable=False)
    color_desc = Column(String(256), nullable=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class VehicleColorLog(Base):
    __tablename__ = 'tbl_vehicle_color_log'
    id = Column(GUID, primary_key=True, index=True)
    vehicle_color_id = Column(GUID, ForeignKey(VehicleColors.id, deferrable=True), nullable=False, index=True)
    action = Column(Enum(VehicleColorAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class VehicleTypes(Base):
    __tablename__ = 'tbl_vehicle_type'
    id = Column(GUID, primary_key=True, index=True)
    type_name = Column(String(256), nullable=False)
    type_desc = Column(String(256), nullable=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class VehicleTypeLog(Base):
    __tablename__ = 'tbl_vehicle_type_log'
    id = Column(GUID, primary_key=True, index=True)
    vehicle_type_id = Column(GUID, ForeignKey(VehicleTypes.id, deferrable=True), nullable=False, index=True)
    action = Column(Enum(VehicleTypeAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class Vehicles(Base):
    __tablename__ = "tbl_vehicle"
    id = Column(GUID, primary_key=True, index=True)
    model_id = Column(GUID, ForeignKey(VehicleModels.id, deferrable=True), nullable=False)
    type_id = Column(GUID, ForeignKey(VehicleTypes.id, deferrable=True), nullable=False)
    vehicle_name = Column(String(256), nullable=False, index=True)
    document_no = Column(String(64), nullable=True, index=True)
    vehicle_no = Column(String(64), nullable=False, index=True)
    vehicle_year = Column(Integer(), nullable=True, index=True)
    vehicle_color = Column(String(256), nullable=True)
    engine_no = Column(String(64), nullable=True)
    body_no = Column(String(64), nullable=True)
    max_weight = Column(String(64), nullable=True)
    net_weight = Column(String(64), nullable=True)
    validity = Column(String(64), nullable=True)
    vehicle_desc = Column(String(512), nullable=True)
    driver_id = Column(GUID, ForeignKey(Customers.id, deferrable=True), nullable=True, index=True)
    search_meta = Column(ARRAY(Text), nullable=True, index=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class VehicleLog(Base):
    __tablename__ = 'tbl_vehicle_log'
    id = Column(GUID, primary_key=True, index=True)
    vehicle_id = Column(GUID, ForeignKey(Vehicles.id, deferrable=True), nullable=False, index=True)
    action = Column(Enum(VehicleAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class Shifts(Base):
    __tablename__ = 'tbl_shift'
    id = Column(GUID, primary_key=True, index=True)
    shift_name = Column(String(256), nullable=False)
    shift_desc = Column(String(256), nullable=True)
    shift_start_time = Column(DateTime(), nullable=False, index=True)
    shift_end_time = Column(DateTime(), nullable=False, index=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class ShiftLog(Base):
    __tablename__ = 'tbl_shift_log'
    id = Column(GUID, primary_key=True, index=True)
    shift_id = Column(GUID, ForeignKey(Shifts.id, deferrable=True), nullable=False, index=True)
    action = Column(Enum(ShiftAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class ShiftVehicles(Base):
    __tablename__ = 'tbl_shift_vehicles'
    id = Column(GUID, primary_key=True, index=True)
    shift_id = Column(GUID, ForeignKey(Shifts.id, deferrable=True), nullable=False, index=True)
    vehicle_id = Column(GUID, ForeignKey(Vehicles.id, deferrable=True), nullable=False, index=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class ShiftVehicleLog(Base):
    __tablename__ = 'tbl_shift_vehicles_log'
    id = Column(GUID, primary_key=True, index=True)
    shift_vehicle_id = Column(GUID, ForeignKey(ShiftVehicles.id, deferrable=True), nullable=False, index=True)
    action = Column(Enum(ShiftVehicleAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class Services(Base):
    __tablename__ = 'tbl_service'
    id = Column(GUID, primary_key=True, index=True)
    service_name = Column(String(256), nullable=False)
    service_desc = Column(String(256), nullable=True)
    service_priority = Column(Integer(), nullable=False, default=1)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class ServiceLog(Base):
    __tablename__ = 'tbl_service_log'
    id = Column(GUID, primary_key=True, index=True)
    service_id = Column(GUID, ForeignKey(Services.id, deferrable=True), nullable=False, index=True)
    action = Column(Enum(ServiceAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class ServiceVehicles(Base):
    __tablename__ = 'tbl_service_vehicles'
    id = Column(GUID, primary_key=True, index=True)
    service_id = Column(GUID, ForeignKey(Services.id, deferrable=True), nullable=False, index=True)
    vehicle_id = Column(GUID, ForeignKey(Vehicles.id, deferrable=True), nullable=False, index=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class ServiceVehicleLog(Base):
    __tablename__ = 'tbl_service_vehicles_log'
    id = Column(GUID, primary_key=True, index=True)
    service_vehicle_id = Column(GUID, ForeignKey(ServiceVehicles.id, deferrable=True), nullable=False, index=True)
    action = Column(Enum(ServiceVehicleAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class Rates(Base):
    __tablename__ = "tbl_rate"
    id = Column(GUID, primary_key=True, index=True)
    rate_name = Column(String(256), nullable=False)
    rate_desc = Column(String(256), nullable=True)
    service_id = Column(GUID, ForeignKey(Services.id, deferrable=True), nullable=False, index=True)
    shift_id = Column(GUID, ForeignKey(Shifts.id, deferrable=True), nullable=False, index=True)
    district_ids = Column(ARRAY(GUID), nullable=True)
    district_names = Column(ARRAY(String(256)), nullable=True)
    start_date = Column(Date(), nullable=False)
    end_date = Column(Date(), nullable=False)
    price_km = Column(Float(), nullable=False)
    price_min = Column(Float(), nullable=False)
    price_wait_min = Column(Float(), nullable=False)
    minute_free_wait = Column(Float(), nullable=False)
    km_free = Column(Float(), nullable=False)
    price_delivery = Column(Float(), nullable=False)
    minute_for_wait = Column(Float(), nullable=False)
    price_cancel = Column(Float(), nullable=False)
    price_minimal = Column(Float(), nullable=False)
    service_prc = Column(Float(), nullable=False)
    birthday_discount_prc = Column(Float(), nullable=False)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class RateLog(Base):
    __tablename__ = 'tbl_rate_log'
    id = Column(GUID, primary_key=True, index=True)
    rate_id = Column(GUID, ForeignKey(Rates.id, deferrable=True), nullable=False, index=True)
    action = Column(Enum(RateAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class Districts(Base):
    __tablename__ = "tbl_district"
    id = Column(GUID, primary_key=True, index=True)
    district_name = Column(String(256), nullable=False)
    district_desc = Column(String(256), nullable=True)
    district_geo = Column(Geometry(geometry_type="POLYGON", srid=4326, spatial_index=True), nullable=True, index=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class DistrictLog(Base):
    __tablename__ = 'tbl_district_log'
    id = Column(GUID, primary_key=True, index=True)
    district_id = Column(GUID, ForeignKey(Districts.id, deferrable=True), nullable=False, index=True)
    action = Column(Enum(DistrictAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class Orders(Base):
    __tablename__ = "tbl_order"
    id = Column(GUID, primary_key=True)
    driver_id = Column(GUID, ForeignKey(Customers.id, deferrable=True), nullable=True, index=True)
    vehicle_id = Column(GUID, ForeignKey(Vehicles.id, deferrable=True), nullable=True, index=True)
    client_id = Column(GUID, ForeignKey(Customers.id, deferrable=True), nullable=True, index=True)
    service_id = Column(GUID, ForeignKey(Services.id, deferrable=True), nullable=True, index=True)
    shift_id = Column(GUID, ForeignKey(Shifts.id, deferrable=True), nullable=True, index=True)
    rate_id = Column(GUID, ForeignKey(Rates.id, deferrable=True), nullable=True, index=True)
    district_id_from = Column(GUID, ForeignKey(Districts.id, deferrable=True), nullable=True, index=True)
    district_id_to = Column(GUID, ForeignKey(Districts.id, deferrable=True), nullable=True, index=True)
    order_address_from = Column(JSONB, nullable=True)
    order_address_to = Column(JSONB, nullable=True)
    order_code = Column(String(32), nullable=True)
    order_desc = Column(String(256), nullable=True)
    order_date = Column(DateTime(), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    order_state = Column(Enum(OrderState), nullable=False)
    pay_total = Column(Float(), nullable=True, default=0)
    pay_discount_prc = Column(Float(), nullable=True, default=0)
    pay_discount_amount = Column(Float(), nullable=True, default=0)
    pay_net_total = Column(Float(), nullable=True, default=0)
    pay_net_total_text = Column(String(512), nullable=True)
    service_prc = Column(Float(), nullable=True, default=0)
    service_amount = Column(Float(), nullable=True, default=0)
    order_distance = Column(Float(), nullable=True)  # in km
    order_time = Column(Float(), nullable=True)  # in seconds
    order_wait_time = Column(Float(), nullable=True)  # in seconds
    canceled_vehicles = Column(ARRAY(GUID), nullable=True, index=True)
    order_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=True, index=True)
    create_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False, index=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class OrderLog(Base):
    __tablename__ = 'tbl_order_log'
    id = Column(GUID, primary_key=True, index=True)
    order_id = Column(GUID, ForeignKey(Orders.id, deferrable=True), nullable=False, index=True)
    action = Column(Enum(OrderAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class OrderHistory(Base):
    __tablename__ = "tbl_order_history"
    id = Column(GUID, primary_key=True, index=True)
    order_id = Column(GUID, ForeignKey(Orders.id, deferrable=True), nullable=False, index=True)
    order_date = Column(DateTime(), nullable=False)
    order_state = Column(Enum(OrderState), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class ClientAddressHistory(Base):
    __tablename__ = "tbl_client_address_history"
    id = Column(GUID, primary_key=True, index=True)
    client_id = Column(GUID, ForeignKey(Customers.id, deferrable=True), nullable=True, index=True)
    district_id = Column(GUID, ForeignKey(Districts.id, deferrable=True), nullable=True, index=True)
    address_type = Column(Enum(AddressType), nullable=False)
    address = Column(Text(), nullable=True, index=True)
    coordinates = Column(Text(), nullable=True, index=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class VehicleStatus(Base):
    __tablename__ = "tbl_vehicle_status"
    id = Column(GUID, primary_key=True)
    driver_id = Column(GUID, ForeignKey(Customers.id, deferrable=True), nullable=False, index=True)
    vehicle_id = Column(GUID, ForeignKey(Vehicles.id, deferrable=True), nullable=False, index=True)
    service_ids = Column(ARRAY(GUID), nullable=True, index=True)
    district_id = Column(GUID, ForeignKey(Districts.id, deferrable=True), nullable=True, index=True)
    vehicle_available = Column(Enum(VehicleAvailable), nullable=False, index=True)
    vehicle_state = Column(Enum(VehicleState), nullable=False, index=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class Payments(Base):
    __tablename__ = "tbl_payment"
    id = Column(GUID, primary_key=True)
    payment_method = Column(Enum(PaymentMethods), nullable=False)
    customer_id = Column(GUID, ForeignKey(Customers.id, deferrable=True), nullable=True)
    payment_code = Column(String(32), nullable=False)
    payment_amount = Column(Float(), nullable=False)
    payment_amount_text = Column(String(256), nullable=True)
    payment_date = Column(DateTime(timezone=False), nullable=False)
    payment_desc = Column(String(256), nullable=True)
    in_out = Column(Boolean, nullable=False)
    create_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)


class PaymentLog(Base):
    __tablename__ = 'tbl_payment_log'
    id = Column(GUID, primary_key=True)
    payment_id = Column(GUID, ForeignKey(Payments.id, deferrable=True), nullable=False)
    action = Column(Enum(PaymentAction), nullable=False)
    action_user = Column(String(64), ForeignKey(Users.username, deferrable=True), nullable=False)
    sup_info = Column(Text(), nullable=False)
    action_ts = Column(DateTime(timezone=False), nullable=False)


class DriverVehicleLocation(Base):
    __tablename__ = "tbl_driver_vehicle_location"
    id = Column(GUID, primary_key=True)
    driver_id = Column(GUID, ForeignKey(Customers.id, deferrable=True), nullable=False, index=True)
    vehicle_id = Column(GUID, ForeignKey(Vehicles.id, deferrable=True), nullable=True, index=True)
    order_id = Column(GUID, ForeignKey(Orders.id, deferrable=True), nullable=True, index=True)
    geo_location = Column(Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=True, index=True)
    district_id = Column(GUID, ForeignKey(Districts.id, deferrable=True), nullable=True, index=True)
    create_ts = Column(DateTime(timezone=False), nullable=False)


class CustomerRatings(Base):
    __tablename__ = 'tbl_customer_rating'
    id = Column(GUID, primary_key=True)
    set_customer_id = Column(GUID, ForeignKey(Customers.id, deferrable=True), nullable=True, index=True)
    get_customer_id = Column(GUID, ForeignKey(Customers.id, deferrable=True), nullable=True, index=True)
    rating = Column(Integer(), nullable=False, default=0)
    comment = Column(Text(), nullable=True)
    state = Column(Enum(EntityState), nullable=False)
    create_ts = Column(DateTime(timezone=False), nullable=False)
    update_ts = Column(DateTime(timezone=False), nullable=False)

    set_customers = relationship("Customers", foreign_keys=[set_customer_id])
    get_customers = relationship("Customers", foreign_keys=[get_customer_id])

    @hybrid_property
    def set_username(self):
        if self.set_customers:
            return self.set_customers.username
        else:
            return ""

    @hybrid_property
    def get_username(self):
        if self.get_customers:
            return self.get_customers.username
        else:
            return ""

    @set_username.expression
    def set_username(cls):
        return select([Customers.username]).where(Customers.id == cls.set_customer_id).as_scalar()

    @get_username.expression
    def get_username(cls):
        return select([Customers.username]).where(Customers.id == cls.get_customer_id).as_scalar()
# endregion
