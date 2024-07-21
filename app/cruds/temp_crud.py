import json
import uuid
from datetime import datetime

from sqlalchemy import func, case, and_
from sqlalchemy.orm import Session

from app import models


# region Samples
def shift_vehicle_view_sample(db: Session):
    join_query = db.query(models.ShiftVehicles.id,
                          models.ShiftVehicles.shift_id,
                          models.ShiftVehicles.vehicle_id,
                          models.ShiftVehicles.state,
                          models.ShiftVehicles.create_ts,
                          models.ShiftVehicles.update_ts,
                          models.Shifts.shift_name,
                          models.Shifts.shift_desc,
                          models.Shifts.shift_start_time,
                          models.Shifts.shift_end_time,
                          models.Vehicles.vehicle_name,
                          models.VehicleTypes.type_name,
                          models.Customers.fullname,
                          case(
                              [
                                  (models.VehicleStatus.id == None,
                                   False),
                                  (models.VehicleStatus.vehicle_state == models.VehicleState.disable,
                                   False)
                              ],
                              else_=True).label("vehicle_state")
                          ) \
        .join(models.Shifts, models.Shifts.id == models.ShiftVehicles.shift_id) \
        .join(models.Vehicles, models.Vehicles.id == models.ShiftVehicles.vehicle_id) \
        .join(models.VehicleTypes, models.VehicleTypes.id == models.Vehicles.type_id) \
        .outerjoin(models.Customers, models.Customers.id == models.Vehicles.driver_id) \
        .outerjoin(models.VehicleStatus, models.VehicleStatus.vehicle_id == models.ShiftVehicles.vehicle_id)
    return join_query


def service_vehicle_view_sample(db: Session):
    join_query = db.query(models.ServiceVehicles.id,
                          models.ServiceVehicles.service_id,
                          models.ServiceVehicles.vehicle_id,
                          models.ServiceVehicles.state,
                          models.ServiceVehicles.create_ts,
                          models.ServiceVehicles.update_ts,
                          models.Services.service_name,
                          models.Services.service_desc,
                          models.Vehicles.vehicle_name,
                          models.VehicleTypes.type_name,
                          models.Customers.fullname) \
        .join(models.Services, models.Services.id == models.ServiceVehicles.service_id) \
        .join(models.Vehicles, models.Vehicles.id == models.ServiceVehicles.vehicle_id) \
        .join(models.VehicleTypes, models.VehicleTypes.id == models.Vehicles.type_id) \
        .outerjoin(models.Customers, models.Customers.id == models.Vehicles.driver_id)
    return join_query


def rate_view_sample(db: Session):
    join_query = db.query(models.Rates.id,
                          models.Rates.rate_name,
                          models.Rates.rate_desc,
                          models.Rates.service_id,
                          models.Rates.shift_id,
                          models.Rates.district_ids,
                          models.Rates.district_names,
                          models.Rates.start_date,
                          models.Rates.end_date,
                          models.Rates.price_km,
                          models.Rates.price_min,
                          models.Rates.price_wait_min,
                          models.Rates.minute_free_wait,
                          models.Rates.km_free,
                          models.Rates.price_delivery,
                          models.Rates.minute_for_wait,
                          models.Rates.price_cancel,
                          models.Rates.price_minimal,
                          models.Rates.service_prc,
                          models.Rates.birthday_discount_prc,
                          models.Rates.state,
                          models.Rates.create_ts,
                          models.Rates.update_ts,
                          models.Services.service_name,
                          models.Services.service_desc,
                          models.Shifts.shift_name,
                          models.Shifts.shift_desc,
                          models.Shifts.shift_start_time,
                          models.Shifts.shift_end_time) \
        .join(models.Services, models.Services.id == models.Rates.service_id) \
        .join(models.Shifts, models.Shifts.id == models.Rates.shift_id)
    return join_query


# endregion


# region Shifts
def add_shift(db: Session, shift_name, shift_desc, shift_start_time, shift_end_time, action_user):
    db_shift = models.Shifts(id=uuid.uuid4(),
                             shift_name=shift_name,
                             shift_desc=shift_desc,
                             shift_start_time=shift_start_time,
                             shift_end_time=shift_end_time,
                             state=models.EntityState.active.name,
                             create_ts=datetime.now(),
                             update_ts=datetime.now())
    db.add(db_shift)
    db.flush()
    shift_json_info = {'shift_name': str(shift_name),
                       'shift_desc': str(shift_desc),
                       'shift_start_time': str(shift_start_time),
                       'shift_end_time': str(shift_end_time)}
    db_shift_log = models.ShiftLog(id=uuid.uuid4(),
                                   shift_id=db_shift.id,
                                   action=models.ShiftAction.ShiftAdd,
                                   action_user=action_user,
                                   sup_info=json.dumps(shift_json_info),
                                   action_ts=datetime.now())
    db.add(db_shift_log)
    return db_shift.id


def edit_shift(db: Session, id, shift_name, shift_desc, shift_start_time, shift_end_time, action_user):
    db_shift = db.query(models.Shifts).filter(models.Shifts.id == id)
    edit_shift_crud = {
        models.Shifts.shift_name: shift_name,
        models.Shifts.shift_desc: shift_desc,
        models.Shifts.shift_start_time: shift_start_time,
        models.Shifts.shift_end_time: shift_end_time,
        models.Shifts.update_ts: datetime.now()
    }
    db_shift.update(edit_shift_crud)
    shift_json_info = {'shift_name': str(shift_name),
                       'shift_desc': str(shift_desc),
                       'shift_start_time': str(shift_start_time),
                       'shift_end_time': str(shift_end_time)}
    db_shift_log = models.ShiftLog(id=uuid.uuid4(),
                                   shift_id=id,
                                   action=models.ShiftAction.ShiftEdit,
                                   action_user=action_user,
                                   sup_info=json.dumps(shift_json_info),
                                   action_ts=datetime.now())
    db.add(db_shift_log)
    return id


def change_shift_state(db: Session, id, state, action_user):
    db_shift = db.query(models.Shifts).filter(models.Shifts.id == id)
    edit_shift_crud = {
        models.Shifts.state: state,
        models.Shifts.update_ts: datetime.now()
    }
    db_shift.update(edit_shift_crud)
    shift_json_info = {'state': state.name}
    db_shift_log = models.ShiftLog(id=uuid.uuid4(),
                                   shift_id=id,
                                   action=models.ShiftAction.ShiftStateChange,
                                   action_user=action_user,
                                   sup_info=json.dumps(shift_json_info),
                                   action_ts=datetime.now())
    db.add(db_shift_log)
    return id


def get_shift_by_id(db: Session, id):
    db_shift = db.query(models.Shifts).get(id)
    return db_shift


def get_shift_list(db: Session):
    db_shift = db.query(models.Shifts) \
        .order_by(models.Shifts.shift_name)
    return db_shift.all()


def get_shift_active_list(db: Session):
    db_shift = db.query(models.Shifts) \
        .filter(models.Shifts.state == models.EntityState.active) \
        .order_by(models.Shifts.shift_name)
    return db_shift.all()


def get_active_shift_search(db: Session, search_text):
    db_shift = db.query(models.Shifts) \
        .filter(models.Shifts.state == models.EntityState.active) \
        .filter(func.concat(models.Shifts.shift_name,
                            ' ', models.Shifts.shift_desc).ilike('%' + search_text + '%')) \
        .order_by(models.Shifts.shift_name)
    return db_shift.all()


# endregion


# region Shift Vehicles
def add_shift_vehicle(db: Session, shift_id, vehicle_id, action_user):
    db_shift_vehicle = models.ShiftVehicles(id=uuid.uuid4(),
                                            shift_id=shift_id,
                                            vehicle_id=vehicle_id,
                                            state=models.EntityState.active.name,
                                            create_ts=datetime.now(),
                                            update_ts=datetime.now())
    db.add(db_shift_vehicle)
    db.flush()
    shift_vehicle_json_info = {'shift_id': str(shift_id),
                               'vehicle_id': str(vehicle_id)}
    db_shift_vehicle_log = models.ShiftVehicleLog(id=uuid.uuid4(),
                                                  shift_vehicle_id=db_shift_vehicle.id,
                                                  action=models.ShiftVehicleAction.ShiftVehicleAdd,
                                                  action_user=action_user,
                                                  sup_info=json.dumps(shift_vehicle_json_info),
                                                  action_ts=datetime.now())
    db.add(db_shift_vehicle_log)
    return db_shift_vehicle.id


def change_shift_vehicle_state(db: Session, id, state, action_user):
    db_shift_vehicle = db.query(models.ShiftVehicles).filter(models.ShiftVehicles.id == id)
    edit_shift_vehicle_crud = {
        models.ShiftVehicles.state: state,
        models.ShiftVehicles.update_ts: datetime.now()
    }
    db_shift_vehicle.update(edit_shift_vehicle_crud)
    shift_vehicle_json_info = {'state': state.name}
    db_shift_vehicle_log = models.ShiftVehicleLog(id=uuid.uuid4(),
                                                  shift_vehicle_id=id,
                                                  action=models.ShiftVehicleAction.ShiftVehicleStateChange,
                                                  action_user=action_user,
                                                  sup_info=json.dumps(shift_vehicle_json_info),
                                                  action_ts=datetime.now())
    db.add(db_shift_vehicle_log)
    return id


def get_shift_vehicle_by_id(db: Session, id):
    db_shift_vehicle = db.query(models.ShiftVehicles).get(id)
    return db_shift_vehicle


def get_shift_vehicle_by_info(db: Session, shift_id, vehicle_id):
    db_shift_vehicle = db.query(models.ShiftVehicles) \
        .filter(models.ShiftVehicles.shift_id == shift_id) \
        .filter(models.ShiftVehicles.vehicle_id == vehicle_id)
    return db_shift_vehicle.first()


def get_shift_vehicle_list(db: Session):
    db_shift_vehicle = db.query(models.ShiftVehicles) \
        .order_by(models.ShiftVehicles.shift_id)
    return db_shift_vehicle.all()


def get_shift_vehicle_active_list(db: Session):
    db_shift_vehicle = db.query(models.ShiftVehicles) \
        .filter(models.ShiftVehicles.state == models.EntityState.active) \
        .order_by(models.ShiftVehicles.shift_id)
    return db_shift_vehicle.all()


def get_active_shift_vehicle_search(db: Session, search_text):
    db_shift_vehicle = shift_vehicle_view_sample(db) \
        .filter(models.ShiftVehicles.state == models.EntityState.active) \
        .filter(func.concat(models.Vehicles.vehicle_name["ru"],
                            ' ', models.Vehicles.vehicle_name["tm"],
                            ' ', models.Vehicles.vehicle_name["en"]).ilike('%' + search_text + '%')) \
        .order_by(models.Vehicles.vehicle_no)
    return db_shift_vehicle.all()


def get_active_shift_vehicle_search_by_shift(db: Session, search_text, shift_id):
    db_shift_vehicle = shift_vehicle_view_sample(db) \
        .filter(models.ShiftVehicles.state == models.EntityState.active) \
        .filter(models.ShiftVehicles.shift_id == shift_id) \
        .filter(func.concat(models.Vehicles.vehicle_name["ru"],
                            ' ', models.Vehicles.vehicle_name["tm"],
                            ' ', models.Vehicles.vehicle_name["en"]).ilike('%' + search_text + '%')) \
        .order_by(models.Vehicles.vehicle_no)
    return db_shift_vehicle.all()


# endregion


# region Services
def add_service(db: Session, service_name, service_desc, service_priority, action_user):
    db_service = models.Services(id=uuid.uuid4(),
                                 service_name=service_name,
                                 service_desc=service_desc,
                                 service_priority=service_priority,
                                 state=models.EntityState.active.name,
                                 create_ts=datetime.now(),
                                 update_ts=datetime.now())
    db.add(db_service)
    db.flush()
    service_json_info = {'service_name': str(service_desc),
                         'service_desc': str(service_desc),
                         'service_priority': service_priority}
    db_service_log = models.ServiceLog(id=uuid.uuid4(),
                                       service_id=db_service.id,
                                       action=models.ServiceAction.ServiceAdd,
                                       action_user=action_user,
                                       sup_info=json.dumps(service_json_info),
                                       action_ts=datetime.now())
    db.add(db_service_log)
    return db_service.id


def edit_service(db: Session, id, service_name, service_desc, service_priority, action_user):
    db_service = db.query(models.Services).filter(models.Services.id == id)
    edit_service_crud = {
        models.Services.service_name: service_name,
        models.Services.service_desc: service_desc,
        models.Services.service_priority: service_priority,
        models.Services.update_ts: datetime.now()
    }
    db_service.update(edit_service_crud)
    service_json_info = {'service_name': str(service_desc),
                         'service_desc': str(service_desc),
                         'service_priority': service_priority}
    db_service_log = models.ServiceLog(id=uuid.uuid4(),
                                       service_id=id,
                                       action=models.ServiceAction.ServiceEdit,
                                       action_user=action_user,
                                       sup_info=json.dumps(service_json_info),
                                       action_ts=datetime.now())
    db.add(db_service_log)
    return id


def change_service_state(db: Session, id, state, action_user):
    db_service = db.query(models.Services).filter(models.Services.id == id)
    edit_service_crud = {
        models.Services.state: state,
        models.Services.update_ts: datetime.now()
    }
    db_service.update(edit_service_crud)
    service_json_info = {'state': state.name}
    db_service_log = models.ServiceLog(id=uuid.uuid4(),
                                       service_id=id,
                                       action=models.ServiceAction.ServiceStateChange,
                                       action_user=action_user,
                                       sup_info=json.dumps(service_json_info),
                                       action_ts=datetime.now())
    db.add(db_service_log)
    return id


def get_service_by_id(db: Session, id):
    db_service = db.query(models.Services).get(id)
    return db_service


def get_service_list(db: Session):
    db_service = db.query(models.Services) \
        .order_by(models.Services.service_priority)
    return db_service.all()


def get_service_active_list(db: Session):
    db_service = db.query(models.Services) \
        .filter(models.Services.state == models.EntityState.active) \
        .order_by(models.Services.service_priority)
    return db_service.all()


def get_active_service_search(db: Session, search_text):
    db_service = db.query(models.Services) \
        .filter(models.Services.state == models.EntityState.active) \
        .filter(func.concat(models.Services.service_name,
                            ' ', models.Services.service_desc).ilike('%' + search_text + '%')) \
        .order_by(models.Services.service_priority)
    return db_service.all()


# endregion


# region Service Vehicles
def add_service_vehicle(db: Session, service_id, vehicle_id, action_user):
    db_service_vehicle = models.ServiceVehicles(id=uuid.uuid4(),
                                                service_id=service_id,
                                                vehicle_id=vehicle_id,
                                                state=models.EntityState.active.name,
                                                create_ts=datetime.now(),
                                                update_ts=datetime.now())
    db.add(db_service_vehicle)
    db.flush()
    service_vehicle_json_info = {'service_id': str(service_id),
                                 'vehicle_id': str(vehicle_id)}
    db_service_vehicle_log = models.ServiceVehicleLog(id=uuid.uuid4(),
                                                      service_vehicle_id=db_service_vehicle.id,
                                                      action=models.ServiceVehicleAction.ServiceVehicleAdd,
                                                      action_user=action_user,
                                                      sup_info=json.dumps(service_vehicle_json_info),
                                                      action_ts=datetime.now())
    db.add(db_service_vehicle_log)
    return db_service_vehicle.id


def change_service_vehicle_state(db: Session, id, state, action_user):
    db_service_vehicle = db.query(models.ServiceVehicles).filter(models.ServiceVehicles.id == id)
    edit_service_vehicle_crud = {
        models.ServiceVehicles.state: state,
        models.ServiceVehicles.update_ts: datetime.now()
    }
    db_service_vehicle.update(edit_service_vehicle_crud)
    service_vehicle_json_info = {'state': state.name}
    db_service_vehicle_log = models.ServiceVehicleLog(id=uuid.uuid4(),
                                                      service_vehicle_id=id,
                                                      action=models.ServiceVehicleAction.ServiceVehicleStateChange,
                                                      action_user=action_user,
                                                      sup_info=json.dumps(service_vehicle_json_info),
                                                      action_ts=datetime.now())
    db.add(db_service_vehicle_log)
    return id


def get_service_vehicle_by_id(db: Session, id):
    db_service_vehicle = db.query(models.ServiceVehicles).get(id)
    return db_service_vehicle


def get_service_vehicle_by_info(db: Session, service_id, vehicle_id):
    db_service_vehicle = db.query(models.ServiceVehicles) \
        .filter(models.ServiceVehicles.service_id == service_id) \
        .filter(models.ServiceVehicles.vehicle_id == vehicle_id)
    return db_service_vehicle.first()


def get_service_vehicle_list(db: Session):
    db_service_vehicle = db.query(models.ServiceVehicles).order_by(models.ServiceVehicles.service_id)
    return db_service_vehicle.all()


def get_service_vehicle_active_list_by_vehicle(db: Session, vehicle_id):
    db_service_vehicle = db.query(models.ServiceVehicles) \
        .filter(models.ServiceVehicles.vehicle_id == vehicle_id) \
        .filter(models.ServiceVehicles.state == models.EntityState.active) \
        .order_by(models.ServiceVehicles.service_id)
    return db_service_vehicle.all()


def get_service_vehicle_active_list(db: Session):
    db_service_vehicle = db.query(models.ServiceVehicles) \
        .filter(models.ServiceVehicles.state == models.EntityState.active) \
        .order_by(models.ServiceVehicles.service_id)
    return db_service_vehicle.all()


def get_active_service_vehicle_search(db: Session, search_text):
    db_service_vehicle = service_vehicle_view_sample(db) \
        .filter(models.ServiceVehicles.state == models.EntityState.active) \
        .filter(func.concat(models.Vehicles.vehicle_name["ru"],
                            ' ', models.Vehicles.vehicle_name["tm"],
                            ' ', models.Vehicles.vehicle_name["en"]).ilike('%' + search_text + '%')) \
        .order_by(models.ServiceVehicles.service_id)
    return db_service_vehicle.all()


def get_active_service_vehicle_search_by_service(db: Session, search_text, service_id):
    db_service_vehicle = service_vehicle_view_sample(db) \
        .filter(models.ServiceVehicles.service_id == service_id) \
        .filter(models.ServiceVehicles.state == models.EntityState.active) \
        .filter(func.concat(models.Vehicles.vehicle_name["ru"],
                            ' ', models.Vehicles.vehicle_name["tm"],
                            ' ', models.Vehicles.vehicle_name["en"]).ilike('%' + search_text + '%')) \
        .order_by(models.ServiceVehicles.service_id)
    return db_service_vehicle.all()


# endregion


# region Districts
def add_district(db: Session, district_name, district_desc, district_geo, action_user):
    db_district = models.Districts(id=uuid.uuid4(),
                                   district_name=district_name,
                                   district_desc=district_desc,
                                   district_geo=district_geo,
                                   state=models.EntityState.active,
                                   create_ts=datetime.now(),
                                   update_ts=datetime.now())
    db.add(db_district)
    db.flush()
    district_json_info = {'district_name': str(district_desc),
                          'district_desc': str(district_desc),
                          'district_geo': 'SRID=4326;' + district_geo}
    db_district_log = models.DistrictLog(id=uuid.uuid4(),
                                         district_id=db_district.id,
                                         action=models.DistrictAction.DistrictAdd,
                                         action_user=action_user,
                                         sup_info=json.dumps(district_json_info),
                                         action_ts=datetime.now())
    db.add(db_district_log)
    return db_district.id


def edit_district(db: Session, id, district_name, district_desc, district_geo, action_user):
    db_district = db.query(models.Districts).filter(models.Districts.id == id)
    edit_district_crud = {
        models.Districts.district_name: district_name,
        models.Districts.district_desc: district_desc,
        models.Districts.district_geo: district_geo,
        models.Districts.update_ts: datetime.now()
    }
    db_district.update(edit_district_crud)
    district_json_info = {'district_name': str(district_desc),
                          'district_desc': str(district_desc),
                          'district_geo': district_geo}
    db_district_log = models.DistrictLog(id=uuid.uuid4(),
                                         district_id=id,
                                         action=models.DistrictAction.DistrictEdit,
                                         action_user=action_user,
                                         sup_info=json.dumps(district_json_info),
                                         action_ts=datetime.now())
    db.add(db_district_log)
    return id


def change_district_state(db: Session, id, state, action_user):
    db_district = db.query(models.Districts).filter(models.Districts.id == id)
    edit_district_crud = {
        models.Districts.state: state,
        models.Districts.update_ts: datetime.now()
    }
    db_district.update(edit_district_crud)
    district_json_info = {'state': state.name}
    db_district_log = models.DistrictLog(id=uuid.uuid4(),
                                         district_id=id,
                                         action=models.DistrictAction.DistrictStateChange,
                                         action_user=action_user,
                                         sup_info=json.dumps(district_json_info),
                                         action_ts=datetime.now())
    db.add(db_district_log)
    return id


def get_district_by_id(db: Session, id):
    db_district = db.query(models.Districts).get(id)
    return db_district


def get_district_list(db: Session):
    db_district = db.query(models.Districts).order_by(models.Districts.district_name["ru"])
    return db_district.all()


def get_district_active_list(db: Session):
    db_district = db.query(models.Districts) \
        .filter(models.Districts.state == models.EntityState.active) \
        .order_by(models.Districts.district_name["ru"])
    return db_district.all()


def get_district_active_list_no_id(db: Session, id):
    db_district = db.query(models.Districts) \
        .filter(models.Districts.id != id) \
        .filter(models.Districts.state == models.EntityState.active) \
        .order_by(models.Districts.district_name["ru"])
    return db_district.all()


def get_district_active_list_with_drivers(db: Session):
    vehicle_location = (db.query(models.DriverVehicleLocation.driver_id,
                                 models.DriverVehicleLocation.vehicle_id,
                                 models.DriverVehicleLocation.order_id,
                                 models.DriverVehicleLocation.geo_location,
                                 models.DriverVehicleLocation.district_id)
                        .filter(models.DriverVehicleLocation.geo_location != None)
                        .distinct(models.DriverVehicleLocation.driver_id,
                                  models.DriverVehicleLocation.vehicle_id)
                        .order_by(models.DriverVehicleLocation.driver_id,
                                  models.DriverVehicleLocation.vehicle_id,
                                  models.DriverVehicleLocation.create_ts.desc())).subquery()
    db_district = db.query(models.Districts.id,
                           models.Districts.district_name,
                           models.Districts.district_desc,
                           func.count(vehicle_location.c.vehicle_id).label("vehicles_count")) \
        .join(vehicle_location, vehicle_location.c.district_id == models.Districts.id) \
        .join(models.VehicleStatus, and_(models.VehicleStatus.driver_id == vehicle_location.c.driver_id,
                                         models.VehicleStatus.vehicle_id == vehicle_location.c.vehicle_id)) \
        .filter(models.Districts.state == models.EntityState.active) \
        .filter(models.VehicleStatus.vehicle_available == models.VehicleAvailable.free) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.VehicleStatus.state == models.EntityState.active) \
        .order_by(models.Districts.district_name["ru"]) \
        .group_by(models.Districts.id,
                  models.Districts.district_name,
                  models.Districts.district_desc)
    return db_district.all()


def get_active_district_search(db: Session, search_text):
    db_district = db.query(models.Districts) \
        .filter(models.Districts.state == models.EntityState.active) \
        .filter(func.concat(models.Districts.district_name["tm"],
                            ' ', models.Districts.district_name["ru"],
                            ' ', models.Districts.district_name["en"],
                            ' ', models.Districts.district_desc["tm"],
                            ' ', models.Districts.district_desc["ru"],
                            ' ', models.Districts.district_desc["en"]).ilike('%' + search_text + '%')) \
        .order_by(models.Districts.district_name["ru"])
    return db_district.all()


def get_district_driver(db: Session, district_id):
    vehicle_location = (db.query(models.DriverVehicleLocation.driver_id,
                                 models.DriverVehicleLocation.vehicle_id,
                                 models.DriverVehicleLocation.order_id,
                                 models.DriverVehicleLocation.geo_location,
                                 models.DriverVehicleLocation.district_id)
                        .filter(models.DriverVehicleLocation.geo_location != None)
                        .distinct(models.DriverVehicleLocation.driver_id,
                                  models.DriverVehicleLocation.vehicle_id)
                        .order_by(models.DriverVehicleLocation.driver_id,
                                  models.DriverVehicleLocation.vehicle_id,
                                  models.DriverVehicleLocation.create_ts.desc())).subquery()
    db_district = db.query(vehicle_location.c.driver_id,
                           models.VehicleStatus.update_ts) \
        .join(models.VehicleStatus, and_(models.VehicleStatus.driver_id == vehicle_location.c.driver_id,
                                         models.VehicleStatus.vehicle_id == vehicle_location.c.vehicle_id)) \
        .filter(vehicle_location.c.district_id == district_id) \
        .filter(models.VehicleStatus.vehicle_available == models.VehicleAvailable.free) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.VehicleStatus.state == models.EntityState.active) \
        .order_by(models.VehicleStatus.update_ts)
    return db_district.all()


# endregion


# region Rates
def add_rate(db: Session, rate_name, rate_desc, service_id, shift_id, district_ids, district_names, start_date,
             end_date, price_km, price_min, price_wait_min, minute_free_wait, km_free, price_delivery, minute_for_wait,
             price_cancel, price_minimal, service_prc, birthday_discount_prc, action_user):
    db_rate = models.Rates(id=uuid.uuid4(),
                           rate_name=rate_name,
                           rate_desc=rate_desc,
                           service_id=service_id,
                           shift_id=shift_id,
                           district_ids=district_ids,
                           district_names=district_names,
                           start_date=start_date,
                           end_date=end_date,
                           price_km=price_km,
                           price_min=price_min,
                           price_wait_min=price_wait_min,
                           minute_free_wait=minute_free_wait,
                           km_free=km_free,
                           price_delivery=price_delivery,
                           minute_for_wait=minute_for_wait,
                           price_cancel=price_cancel,
                           price_minimal=price_minimal,
                           service_prc=service_prc,
                           birthday_discount_prc=birthday_discount_prc,
                           state=models.EntityState.active.name,
                           create_ts=datetime.now(),
                           update_ts=datetime.now())
    db.add(db_rate)
    db.flush()
    rate_json_info = {'rate_name': str(rate_name),
                      'rate_desc': str(rate_desc),
                      'service_id': str(service_id),
                      'shift_id': str(shift_id),
                      'start_date': str(start_date),
                      'end_date': str(end_date),
                      'price_km': str(price_km),
                      'price_min': str(price_min),
                      'minute_free_wait': str(minute_free_wait),
                      'price_delivery': str(price_delivery),
                      'minute_for_wait': str(minute_for_wait),
                      'price_cancel': str(price_cancel),
                      'price_minimal': str(price_minimal),
                      'service_prc': str(service_prc),
                      'birthday_discount_prc': str(birthday_discount_prc)}
    db_rate_log = models.RateLog(id=uuid.uuid4(),
                                 rate_id=db_rate.id,
                                 action=models.RateAction.RateAdd,
                                 action_user=action_user,
                                 sup_info=json.dumps(rate_json_info),
                                 action_ts=datetime.now())
    db.add(db_rate_log)
    return db_rate.id


def edit_rate(db: Session, id, rate_name, rate_desc, service_id, shift_id, district_ids, district_names, start_date,
              end_date, price_km, price_min, minute_free_wait, price_delivery, minute_for_wait, price_cancel,
              price_minimal, service_prc, birthday_discount_prc, action_user):
    db_rate = db.query(models.Rates).filter(models.Rates.id == id)
    edit_rate_crud = {
        models.Rates.rate_name: rate_name,
        models.Rates.rate_desc: rate_desc,
        models.Rates.service_id: service_id,
        models.Rates.shift_id: shift_id,
        models.Rates.district_ids: district_ids,
        models.Rates.district_names: district_names,
        models.Rates.start_date: start_date,
        models.Rates.end_date: end_date,
        models.Rates.price_km: price_km,
        models.Rates.price_min: price_min,
        models.Rates.minute_free_wait: minute_free_wait,
        models.Rates.price_delivery: price_delivery,
        models.Rates.minute_for_wait: minute_for_wait,
        models.Rates.price_cancel: price_cancel,
        models.Rates.price_minimal: price_minimal,
        models.Rates.service_prc: service_prc,
        models.Rates.birthday_discount_prc: birthday_discount_prc,
        models.Rates.update_ts: datetime.now()
    }
    db_rate.update(edit_rate_crud)
    rate_json_info = {'rate_name': str(rate_name),
                      'rate_desc': str(rate_desc),
                      'service_id': str(service_id),
                      'shift_id': str(shift_id),
                      'start_date': str(start_date),
                      'end_date': str(end_date),
                      'price_km': str(price_km),
                      'price_min': str(price_min),
                      'minute_free_wait': str(minute_free_wait),
                      'price_delivery': str(price_delivery),
                      'minute_for_wait': str(minute_for_wait),
                      'price_cancel': str(price_cancel),
                      'price_minimal': str(price_minimal),
                      'service_prc': str(service_prc),
                      'birthday_discount_prc': str(birthday_discount_prc)}
    db_rate_log = models.RateLog(id=uuid.uuid4(),
                                 rate_id=id,
                                 action=models.RateAction.RateEdit,
                                 action_user=action_user,
                                 sup_info=json.dumps(rate_json_info),
                                 action_ts=datetime.now())
    db.add(db_rate_log)
    return id


def change_rate_state(db: Session, id, state, action_user):
    db_rate = db.query(models.Rates).filter(models.Rates.id == id)
    edit_rate_crud = {
        models.Rates.state: state,
        models.Rates.update_ts: datetime.now()
    }
    db_rate.update(edit_rate_crud)
    rate_json_info = {'state': state.name}
    db_rate_log = models.RateLog(id=uuid.uuid4(),
                                 rate_id=id,
                                 action=models.RateAction.RateStateChange,
                                 action_user=action_user,
                                 sup_info=json.dumps(rate_json_info),
                                 action_ts=datetime.now())
    db.add(db_rate_log)
    return id


def get_rate_by_id(db: Session, id):
    db_rate = db.query(models.Rates).get(id)
    return db_rate


def get_rate_by_info(db: Session, service_id, shift_id, district_id, order_date):
    db_rate = db.query(models.Rates) \
        .filter(models.Rates.service_id == service_id) \
        .filter(models.Rates.shift_id == shift_id) \
        .filter(models.Rates.end_date >= order_date) \
        .filter(models.Rates.start_date <= order_date) \
        .filter(models.Rates.state == models.EntityState.active)
    if district_id:
        db_rate = db_rate.filter(models.Rates.district_ids.any(district_id))
    else:
        db_rate = db_rate.filter(models.Rates.district_ids == '{}')
    return db_rate.first()


def get_rate_by_info_service(db: Session, service_id, shift_id, district_id, order_date):
    db_rate = rate_view_sample(db) \
        .filter(models.Rates.service_id == service_id) \
        .filter(models.Rates.shift_id == shift_id) \
        .filter(models.Rates.end_date >= order_date) \
        .filter(models.Rates.start_date <= order_date) \
        .filter(models.Rates.state == models.EntityState.active)
    if district_id:
        db_rate = db_rate.filter(models.Rates.district_ids.any(district_id))
    else:
        db_rate = db_rate.filter(models.Rates.district_ids == '{}')
    return db_rate.first()


def get_rate_list(db: Session):
    db_rate = db.query(models.Rates).order_by(models.Rates.rate_name)
    return db_rate.all()


def get_rate_active_list(db: Session):
    db_rate = db.query(models.Rates) \
        .filter(models.Rates.state == models.EntityState.active) \
        .order_by(models.Rates.rate_name)
    return db_rate.all()


def get_rate_active_list_view(db: Session):
    db_rate = rate_view_sample(db) \
        .filter(models.Rates.state == models.EntityState.active) \
        .order_by(models.Rates.rate_name)
    return db_rate.all()


def get_active_rate_search(db: Session, search_text):
    db_rate = rate_view_sample(db) \
        .filter(models.Rates.state == models.EntityState.active) \
        .filter(func.concat(models.Rates.rate_name,
                            ' ', models.Rates.rate_desc).ilike('%' + search_text + '%')) \
        .order_by(models.Rates.rate_name)
    return db_rate.all()


# endregion
