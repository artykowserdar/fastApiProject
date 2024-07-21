import json
import uuid
from datetime import datetime

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app import models


# region Samples to use
def vehicle_view_sample(db: Session):
    join_query = db.query(models.Vehicles.id,
                          models.Vehicles.model_id,
                          models.Vehicles.type_id,
                          models.Vehicles.vehicle_name,
                          models.Vehicles.document_no,
                          models.Vehicles.vehicle_no,
                          models.Vehicles.vehicle_year,
                          models.Vehicles.vehicle_color,
                          models.Vehicles.engine_no,
                          models.Vehicles.body_no,
                          models.Vehicles.max_weight,
                          models.Vehicles.net_weight,
                          models.Vehicles.validity,
                          models.Vehicles.vehicle_desc,
                          models.Vehicles.driver_id,
                          models.Vehicles.state,
                          models.Vehicles.create_ts,
                          models.Vehicles.update_ts,
                          models.VehicleModels.model_name,
                          models.VehicleTypes.type_name,
                          models.Customers.fullname,
                          models.VehicleColors.id.label("color_id"),
                          models.VehicleStatus.vehicle_available,
                          models.VehicleStatus.vehicle_state) \
        .outerjoin(models.VehicleModels, models.VehicleModels.id == models.Vehicles.model_id) \
        .outerjoin(models.VehicleTypes, models.VehicleTypes.id == models.Vehicles.type_id) \
        .outerjoin(models.Customers, models.Customers.id == models.Vehicles.driver_id) \
        .outerjoin(models.VehicleColors, models.VehicleColors.color_name == models.Vehicles.vehicle_color) \
        .outerjoin(models.VehicleStatus, models.VehicleStatus.vehicle_id == models.Vehicles.id)
    return join_query


def vehicle_service_view_sample(db: Session):
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
    join_query = db.query(models.Vehicles.id,
                          models.Vehicles.model_id,
                          models.Vehicles.type_id,
                          models.Vehicles.vehicle_name,
                          models.Vehicles.document_no,
                          models.Vehicles.vehicle_no,
                          models.Vehicles.vehicle_year,
                          models.Vehicles.vehicle_color,
                          models.Vehicles.engine_no,
                          models.Vehicles.body_no,
                          models.Vehicles.max_weight,
                          models.Vehicles.net_weight,
                          models.Vehicles.validity,
                          models.Vehicles.vehicle_desc,
                          models.Vehicles.driver_id,
                          models.Vehicles.state,
                          models.Vehicles.create_ts,
                          models.Vehicles.update_ts,
                          models.VehicleModels.model_name,
                          models.VehicleTypes.type_name,
                          models.Customers.fullname,
                          models.VehicleColors.id.label("color_id"),
                          models.VehicleStatus.vehicle_available,
                          models.VehicleStatus.vehicle_state,
                          vehicle_location.c.geo_location,
                          vehicle_location.c.order_id,
                          models.Districts.district_name) \
        .outerjoin(models.VehicleModels, models.VehicleModels.id == models.Vehicles.model_id) \
        .outerjoin(models.VehicleTypes, models.VehicleTypes.id == models.Vehicles.type_id) \
        .outerjoin(models.Customers, models.Customers.id == models.Vehicles.driver_id) \
        .outerjoin(models.VehicleColors, models.VehicleColors.color_name == models.Vehicles.vehicle_color) \
        .outerjoin(models.VehicleStatus, models.VehicleStatus.vehicle_id == models.Vehicles.id) \
        .outerjoin(models.ServiceVehicles, models.ServiceVehicles.vehicle_id == models.Vehicles.id) \
        .outerjoin(vehicle_location, and_(vehicle_location.c.driver_id == models.VehicleStatus.driver_id,
                                          vehicle_location.c.vehicle_id == models.VehicleStatus.vehicle_id)) \
        .outerjoin(models.Districts, models.Districts.id == vehicle_location.c.district_id) \
        .group_by(models.Vehicles.id,
                  models.Vehicles.model_id,
                  models.Vehicles.type_id,
                  models.Vehicles.vehicle_name,
                  models.Vehicles.document_no,
                  models.Vehicles.vehicle_no,
                  models.Vehicles.vehicle_year,
                  models.Vehicles.vehicle_color,
                  models.Vehicles.engine_no,
                  models.Vehicles.body_no,
                  models.Vehicles.max_weight,
                  models.Vehicles.net_weight,
                  models.Vehicles.validity,
                  models.Vehicles.vehicle_desc,
                  models.Vehicles.driver_id,
                  models.Vehicles.state,
                  models.Vehicles.create_ts,
                  models.Vehicles.update_ts,
                  models.VehicleModels.model_name,
                  models.VehicleTypes.type_name,
                  models.Customers.fullname,
                  models.VehicleColors.id.label("color_id"),
                  models.VehicleStatus.vehicle_available,
                  models.VehicleStatus.vehicle_state,
                  vehicle_location.c.geo_location,
                  vehicle_location.c.order_id,
                  models.Districts.district_name,
                  models.VehicleStatus.update_ts)
    return join_query


def vehicle_status_view_sample(db: Session):
    join_query = db.query(models.VehicleStatus.id,
                          models.VehicleStatus.driver_id,
                          models.VehicleStatus.vehicle_id,
                          models.VehicleStatus.service_ids,
                          models.VehicleStatus.district_id,
                          models.VehicleStatus.vehicle_available,
                          models.VehicleStatus.vehicle_state,
                          models.Customers.phone,
                          models.Customers.fullname,
                          models.Customers.username) \
        .outerjoin(models.Customers, models.Customers.id == models.VehicleStatus.driver_id) \
        .outerjoin(models.CustomerBalances,
                   models.CustomerBalances.customer_id == models.VehicleStatus.driver_id)
    return join_query


def vehicle_status_view_driver(db: Session, district_id):
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
    join_query = db.query(models.VehicleStatus.id,
                          models.VehicleStatus.driver_id,
                          models.VehicleStatus.vehicle_id,
                          models.VehicleStatus.service_ids,
                          models.VehicleStatus.district_id,
                          models.VehicleStatus.vehicle_available,
                          models.VehicleStatus.vehicle_state,
                          models.Customers.phone,
                          models.Customers.fullname,
                          models.Customers.username) \
        .outerjoin(models.Customers, models.Customers.id == models.VehicleStatus.driver_id) \
        .outerjoin(models.CustomerBalances,
                   models.CustomerBalances.customer_id == models.VehicleStatus.driver_id) \
        .outerjoin(vehicle_location, and_(vehicle_location.c.driver_id == models.VehicleStatus.driver_id,
                                          vehicle_location.c.vehicle_id == models.VehicleStatus.vehicle_id)) \
        .filter(vehicle_location.c.district_id == district_id)
    return join_query


# endregion


# region Vehicle Models
def add_model(db: Session, model_name, model_desc, action_user):
    db_model = models.VehicleModels(id=uuid.uuid4(),
                                    model_name=model_name,
                                    model_desc=model_desc,
                                    state=models.EntityState.active,
                                    create_ts=datetime.now(),
                                    update_ts=datetime.now())
    db.add(db_model)
    db.flush()
    model_json_info = {'model_name': str(model_desc),
                       'model_desc': str(model_desc)}
    db_model_log = models.VehicleModelLog(id=uuid.uuid4(),
                                          vehicle_model_id=db_model.id,
                                          action=models.VehicleModelAction.VehicleModelAdd,
                                          action_user=action_user,
                                          sup_info=json.dumps(model_json_info),
                                          action_ts=datetime.now())
    db.add(db_model_log)
    return db_model.id


def edit_model(db: Session, id, model_name, model_desc, action_user):
    db_model = db.query(models.VehicleModels).filter(models.VehicleModels.id == id)
    edit_model_crud = {
        models.VehicleModels.model_name: model_name,
        models.VehicleModels.model_desc: model_desc,
        models.VehicleModels.update_ts: datetime.now()
    }
    db_model.update(edit_model_crud)
    model_json_info = {'model_name': str(model_desc),
                       'model_desc': str(model_desc)}
    db_model_log = models.VehicleModelLog(id=uuid.uuid4(),
                                          vehicle_model_id=id,
                                          action=models.VehicleModelAction.VehicleModelEdit,
                                          action_user=action_user,
                                          sup_info=json.dumps(model_json_info),
                                          action_ts=datetime.now())
    db.add(db_model_log)
    return id


def change_model_state(db: Session, id, state, action_user):
    db_model = db.query(models.VehicleModels).filter(models.VehicleModels.id == id)
    edit_model_crud = {
        models.VehicleModels.state: state,
        models.VehicleModels.update_ts: datetime.now()
    }
    db_model.update(edit_model_crud)
    model_json_info = {'state': state.name}
    db_model_log = models.VehicleModelLog(id=uuid.uuid4(),
                                          vehicle_model_id=id,
                                          action=models.VehicleModelAction.VehicleModelStateChange,
                                          action_user=action_user,
                                          sup_info=json.dumps(model_json_info),
                                          action_ts=datetime.now())
    db.add(db_model_log)
    return id


def get_model_by_id(db: Session, id):
    db_model = db.query(models.VehicleModels).get(id)
    return db_model


def get_model_list(db: Session):
    db_model = db.query(models.VehicleModels) \
        .order_by(models.VehicleModels.model_name["ru"])
    return db_model.all()


def get_model_active_list(db: Session):
    db_model = db.query(models.VehicleModels) \
        .filter(models.VehicleModels.state == models.EntityState.active) \
        .order_by(models.VehicleModels.model_name["ru"])
    return db_model.all()


def get_active_model_search(db: Session, search_text):
    db_model = db.query(models.VehicleModels) \
        .filter(models.VehicleModels.state == models.EntityState.active) \
        .filter(func.concat(models.VehicleModels.model_name["tm"],
                            ' ', models.VehicleModels.model_name["ru"],
                            ' ', models.VehicleModels.model_name["en"],
                            ' ', models.VehicleModels.model_desc["tm"],
                            ' ', models.VehicleModels.model_desc["ru"],
                            ' ', models.VehicleModels.model_desc["en"]).ilike('%' + search_text + '%')) \
        .order_by(models.VehicleModels.model_name["ru"])
    return db_model.all()


# endregion


# region Vehicle Colors
def add_color(db: Session, color_name, color_desc, action_user):
    db_color = models.VehicleColors(id=uuid.uuid4(),
                                    color_name=color_name,
                                    color_desc=color_desc,
                                    state=models.EntityState.active,
                                    create_ts=datetime.now(),
                                    update_ts=datetime.now())
    db.add(db_color)
    db.flush()
    color_json_info = {'color_name': str(color_desc),
                       'color_desc': str(color_desc)}
    db_color_log = models.VehicleColorLog(id=uuid.uuid4(),
                                          vehicle_color_id=db_color.id,
                                          action=models.VehicleColorAction.VehicleColorAdd,
                                          action_user=action_user,
                                          sup_info=json.dumps(color_json_info),
                                          action_ts=datetime.now())
    db.add(db_color_log)
    return db_color.id


def edit_color(db: Session, id, color_name, color_desc, action_user):
    db_color = db.query(models.VehicleColors).filter(models.VehicleColors.id == id)
    edit_color_crud = {
        models.VehicleColors.color_name: color_name,
        models.VehicleColors.color_desc: color_desc,
        models.VehicleColors.update_ts: datetime.now()
    }
    db_color.update(edit_color_crud)
    color_json_info = {'color_name': str(color_desc),
                       'color_desc': str(color_desc)}
    db_color_log = models.VehicleColorLog(id=uuid.uuid4(),
                                          vehicle_color_id=id,
                                          action=models.VehicleColorAction.VehicleColorEdit,
                                          action_user=action_user,
                                          sup_info=json.dumps(color_json_info),
                                          action_ts=datetime.now())
    db.add(db_color_log)
    return id


def change_color_state(db: Session, id, state, action_user):
    db_color = db.query(models.VehicleColors).filter(models.VehicleColors.id == id)
    edit_color_crud = {
        models.VehicleColors.state: state,
        models.VehicleColors.update_ts: datetime.now()
    }
    db_color.update(edit_color_crud)
    color_json_info = {'state': state.name}
    db_color_log = models.VehicleColorLog(id=uuid.uuid4(),
                                          vehicle_color_id=id,
                                          action=models.VehicleColorAction.VehicleColorStateChange,
                                          action_user=action_user,
                                          sup_info=json.dumps(color_json_info),
                                          action_ts=datetime.now())
    db.add(db_color_log)
    return id


def get_color_by_id(db: Session, id):
    db_color = db.query(models.VehicleColors).get(id)
    return db_color


def get_color_list(db: Session):
    db_color = db.query(models.VehicleColors) \
        .order_by(models.VehicleColors.color_name["ru"])
    return db_color.all()


def get_color_active_list(db: Session):
    db_color = db.query(models.VehicleColors) \
        .filter(models.VehicleColors.state == models.EntityState.active) \
        .order_by(models.VehicleColors.color_name["ru"])
    return db_color.all()


def get_active_color_search(db: Session, search_text):
    db_color = db.query(models.VehicleColors) \
        .filter(models.VehicleColors.state == models.EntityState.active) \
        .filter(func.concat(models.VehicleColors.color_name["tm"],
                            ' ', models.VehicleColors.color_name["ru"],
                            ' ', models.VehicleColors.color_name["en"],
                            ' ', models.VehicleColors.color_desc["tm"],
                            ' ', models.VehicleColors.color_desc["ru"],
                            ' ', models.VehicleColors.color_desc["en"]).ilike('%' + search_text + '%')) \
        .order_by(models.VehicleColors.color_name["ru"])
    return db_color.all()


# endregion


# region Vehicle Types
def add_type(db: Session, type_name, type_desc, action_user):
    db_type = models.VehicleTypes(id=uuid.uuid4(),
                                  type_name=type_name,
                                  type_desc=type_desc,
                                  state=models.EntityState.active,
                                  create_ts=datetime.now(),
                                  update_ts=datetime.now())
    db.add(db_type)
    db.flush()
    type_json_info = {'type_name': str(type_desc),
                      'type_desc': str(type_desc)}
    db_type_log = models.VehicleTypeLog(id=uuid.uuid4(),
                                        vehicle_type_id=db_type.id,
                                        action=models.VehicleTypeAction.VehicleTypeAdd,
                                        action_user=action_user,
                                        sup_info=json.dumps(type_json_info),
                                        action_ts=datetime.now())
    db.add(db_type_log)
    return db_type.id


def edit_type(db: Session, id, type_name, type_desc, action_user):
    db_type = db.query(models.VehicleTypes).filter(models.VehicleTypes.id == id)
    edit_type_crud = {
        models.VehicleTypes.type_name: type_name,
        models.VehicleTypes.type_desc: type_desc,
        models.VehicleTypes.update_ts: datetime.now()
    }
    db_type.update(edit_type_crud)
    type_json_info = {'type_name': str(type_desc),
                      'type_desc': str(type_desc)}
    db_type_log = models.VehicleTypeLog(id=uuid.uuid4(),
                                        vehicle_type_id=id,
                                        action=models.VehicleTypeAction.VehicleTypeEdit,
                                        action_user=action_user,
                                        sup_info=json.dumps(type_json_info),
                                        action_ts=datetime.now())
    db.add(db_type_log)
    return id


def change_type_state(db: Session, id, state, action_user):
    db_type = db.query(models.VehicleTypes).filter(models.VehicleTypes.id == id)
    edit_type_crud = {
        models.VehicleTypes.state: state,
        models.VehicleTypes.update_ts: datetime.now()
    }
    db_type.update(edit_type_crud)
    type_json_info = {'state': state.name}
    db_type_log = models.VehicleTypeLog(id=uuid.uuid4(),
                                        vehicle_type_id=id,
                                        action=models.VehicleTypeAction.VehicleTypeStateChange,
                                        action_user=action_user,
                                        sup_info=json.dumps(type_json_info),
                                        action_ts=datetime.now())
    db.add(db_type_log)
    return id


def get_type_by_id(db: Session, id):
    db_type = db.query(models.VehicleTypes).get(id)
    return db_type


def get_type_list(db: Session):
    db_type = db.query(models.VehicleTypes) \
        .order_by(models.VehicleTypes.type_name["ru"])
    return db_type.all()


def get_type_active_list(db: Session):
    db_type = db.query(models.VehicleTypes) \
        .filter(models.VehicleTypes.state == models.EntityState.active) \
        .order_by(models.VehicleTypes.type_name["ru"])
    return db_type.all()


def get_active_type_search(db: Session, search_text):
    db_type = db.query(models.VehicleTypes) \
        .filter(models.VehicleTypes.state == models.EntityState.active) \
        .filter(func.concat(models.VehicleTypes.type_name["tm"],
                            ' ', models.VehicleTypes.type_name["ru"],
                            ' ', models.VehicleTypes.type_name["en"],
                            ' ', models.VehicleTypes.type_desc["tm"],
                            ' ', models.VehicleTypes.type_desc["ru"],
                            ' ', models.VehicleTypes.type_desc["en"]).ilike('%' + search_text + '%')) \
        .order_by(models.VehicleTypes.type_name["ru"])
    return db_type.all()


# endregion


# region Vehicle
def add_vehicle(db: Session, model_id, type_id, vehicle_name, document_no, vehicle_no, vehicle_year, vehicle_color,
                engine_no, body_no, max_weight, net_weight, validity, vehicle_desc, driver_id, action_user):
    db_vehicle = models.Vehicles(id=uuid.uuid4(),
                                 model_id=model_id,
                                 type_id=type_id,
                                 vehicle_name=vehicle_name,
                                 document_no=document_no,
                                 vehicle_no=vehicle_no,
                                 vehicle_year=vehicle_year,
                                 vehicle_color=vehicle_color,
                                 engine_no=engine_no,
                                 body_no=body_no,
                                 max_weight=max_weight,
                                 net_weight=net_weight,
                                 validity=validity,
                                 vehicle_desc=vehicle_desc,
                                 driver_id=driver_id,
                                 state=models.EntityState.active,
                                 create_ts=datetime.now(),
                                 update_ts=datetime.now())
    db.add(db_vehicle)
    db.flush()
    generate_search_meta(db, db_vehicle.id, vehicle_name, vehicle_year, vehicle_color, engine_no, body_no, document_no)
    vehicle_json_info = {"model_id": str(model_id),
                         "type_id": str(type_id),
                         "vehicle_name": str(vehicle_name),
                         "document_no": str(document_no),
                         "vehicle_no": str(vehicle_no),
                         "vehicle_year": str(vehicle_year),
                         "vehicle_color": str(vehicle_color),
                         "engine_no": str(engine_no),
                         "body_no": str(body_no),
                         "max_weight": str(max_weight),
                         "net_weight": str(net_weight),
                         "validity": str(validity),
                         "vehicle_desc": str(vehicle_desc),
                         "driver_id": str(driver_id)}
    db_vehicle_log = models.VehicleLog(id=uuid.uuid4(),
                                       vehicle_id=db_vehicle.id,
                                       action=models.VehicleAction.VehicleAdd,
                                       action_user=action_user,
                                       sup_info=json.dumps(vehicle_json_info),
                                       action_ts=datetime.now())
    db.add(db_vehicle_log)
    return db_vehicle.id


def edit_vehicle(db: Session, id, model_id, type_id, vehicle_name, document_no, vehicle_no, vehicle_year, vehicle_color,
                 engine_no, body_no, max_weight, net_weight, validity, vehicle_desc, action_user):
    db_vehicle = db.query(models.Vehicles).filter(models.Vehicles.id == id)
    edit_vehicle_crud = {
        models.Vehicles.model_id: model_id,
        models.Vehicles.type_id: type_id,
        models.Vehicles.vehicle_name: vehicle_name,
        models.Vehicles.document_no: document_no,
        models.Vehicles.vehicle_no: vehicle_no,
        models.Vehicles.vehicle_year: vehicle_year,
        models.Vehicles.vehicle_color: vehicle_color,
        models.Vehicles.engine_no: engine_no,
        models.Vehicles.body_no: body_no,
        models.Vehicles.max_weight: max_weight,
        models.Vehicles.net_weight: net_weight,
        models.Vehicles.validity: validity,
        models.Vehicles.vehicle_desc: vehicle_desc,
        models.Vehicles.update_ts: datetime.now()
    }
    db_vehicle.update(edit_vehicle_crud)
    vehicle_json_info = {"model_id": str(model_id),
                         "type_id": str(type_id),
                         "vehicle_name": str(vehicle_name),
                         "document_no": str(document_no),
                         "vehicle_no": str(vehicle_no),
                         "vehicle_year": str(vehicle_year),
                         "vehicle_color": str(vehicle_color),
                         "engine_no": str(engine_no),
                         "body_no": str(body_no),
                         "max_weight": str(max_weight),
                         "net_weight": str(net_weight),
                         "validity": str(validity),
                         "vehicle_desc": str(vehicle_desc)}
    db_vehicle_log = models.VehicleLog(id=uuid.uuid4(),
                                       vehicle_id=id,
                                       action=models.VehicleAction.VehicleEdit,
                                       action_user=action_user,
                                       sup_info=json.dumps(vehicle_json_info),
                                       action_ts=datetime.now())
    db.add(db_vehicle_log)
    return id


def edit_vehicle_driver(db: Session, id, driver_id, action_user):
    db_vehicle = db.query(models.Vehicles).filter(models.Vehicles.id == id)
    edit_vehicle_crud = {
        models.Vehicles.driver_id: driver_id,
        models.Vehicles.update_ts: datetime.now()
    }
    db_vehicle.update(edit_vehicle_crud)
    vehicle_json_info = {"model_id": str(driver_id)}
    db_vehicle_log = models.VehicleLog(id=uuid.uuid4(),
                                       vehicle_id=id,
                                       action=models.VehicleAction.VehicleEdit,
                                       action_user=action_user,
                                       sup_info=json.dumps(vehicle_json_info),
                                       action_ts=datetime.now())
    db.add(db_vehicle_log)
    return id


def change_vehicle_state(db: Session, id, state, action_user):
    db_vehicle = db.query(models.Vehicles).filter(models.Vehicles.id == id)
    edit_vehicle_crud = {
        models.Vehicles.state: state,
        models.Vehicles.update_ts: datetime.now()
    }
    db_vehicle.update(edit_vehicle_crud)
    vehicle_json_info = {'state': state.name}
    db_vehicle_log = models.VehicleLog(id=uuid.uuid4(),
                                       vehicle_id=id,
                                       action=models.VehicleAction.VehicleStateChange,
                                       action_user=action_user,
                                       sup_info=json.dumps(vehicle_json_info),
                                       action_ts=datetime.now())
    db.add(db_vehicle_log)
    return id


def get_vehicle_by_id(db: Session, id):
    db_vehicle = vehicle_view_sample(db) \
        .filter(models.Vehicles.id == id)
    return db_vehicle.first()


def get_vehicle_by_id_simple(db: Session, id):
    db_vehicle = db.query(models.Vehicles).get(id)
    return db_vehicle


def get_vehicle_by_no(db: Session, vehicle_no):
    db_vehicle = db.query(models.Vehicles) \
        .filter(models.Vehicles.vehicle_no == vehicle_no)
    return db_vehicle.first()


def get_vehicle_by_no_with_id(db: Session, id, vehicle_no):
    db_vehicle = db.query(models.Vehicles) \
        .filter(models.Vehicles.id != id) \
        .filter(models.Vehicles.vehicle_no == vehicle_no)
    return db_vehicle.first()


def get_vehicle_list(db: Session):
    db_vehicle = db.query(models.Vehicles) \
        .order_by(models.Vehicles.vehicle_name)
    return db_vehicle.all()


def get_vehicle_active_list(db: Session):
    db_vehicle = db.query(models.Vehicles) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def get_vehicle_active_list_no_driver(db: Session):
    db_vehicle = db.query(models.Vehicles) \
        .filter(models.Vehicles.driver_id == None) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def get_vehicle_active_list_no_shift(db: Session, shift_id):
    db_vehicle = db.query(models.Vehicles) \
        .outerjoin(models.ShiftVehicles, and_(models.ShiftVehicles.vehicle_id == models.Vehicles.id,
                                              models.ShiftVehicles.state == models.EntityState.active,
                                              models.ShiftVehicles.shift_id == shift_id)) \
        .filter(models.ShiftVehicles.id == None) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def get_vehicle_active_list_no_service(db: Session, service_id):
    db_vehicle = vehicle_view_sample(db) \
        .outerjoin(models.ServiceVehicles, and_(models.ServiceVehicles.vehicle_id == models.Vehicles.id,
                                                models.ServiceVehicles.state == models.EntityState.active,
                                                models.ServiceVehicles.service_id == service_id)) \
        .filter(models.ServiceVehicles.id == None) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def get_vehicle_active_list_by_driver(db: Session, driver_id):
    db_vehicle = db.query(models.Vehicles) \
        .filter(models.Vehicles.driver_id == driver_id) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def get_vehicle_list_view(db: Session):
    db_vehicle = vehicle_view_sample(db) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def get_vehicle_active_list_view(db: Session):
    db_vehicle = vehicle_view_sample(db) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def get_vehicle_active_list_view_by_driver(db: Session, driver_id):
    db_vehicle = vehicle_view_sample(db) \
        .filter(models.Vehicles.driver_id == driver_id) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def get_vehicle_active_list_view_available(db: Session):
    db_vehicle = vehicle_view_sample(db) \
        .filter(models.VehicleStatus.vehicle_available == models.VehicleAvailable.free) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def get_vehicle_active_list_view_active(db: Session):
    db_vehicle = vehicle_view_sample(db) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def get_vehicle_active_list_view_active_driver(db: Session, driver_id):
    db_vehicle = vehicle_view_sample(db) \
        .filter(models.VehicleStatus.driver_id != driver_id) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def search_vehicle_active(db: Session, search_text):
    db_vehicle = vehicle_view_sample(db) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .filter(func.array_to_string(models.Vehicles.search_meta, ',').ilike('%' + search_text + '%')) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def search_vehicle_active_by_type(db: Session, search_text, type_id):
    db_vehicle = vehicle_view_sample(db) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .filter(func.array_to_string(models.Vehicles.search_meta, ',').ilike('%' + search_text + '%'))
    if type_id:
        db_vehicle = db_vehicle.filter(models.Vehicles.type_id == type_id)
    db_vehicle = db_vehicle.order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def search_vehicle_active_by_service(db: Session, search_text, service_id):
    db_vehicle = vehicle_service_view_sample(db) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .filter(func.array_to_string(models.Vehicles.search_meta, ',').ilike('%' + search_text + '%'))
    if service_id:
        db_vehicle = db_vehicle.filter(models.ServiceVehicles.service_id == service_id)
    db_vehicle = db_vehicle.order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def search_vehicle_active_by_service_available(db: Session, search_text, service_id):
    db_vehicle = vehicle_service_view_sample(db) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(func.array_to_string(models.Vehicles.search_meta, ',').ilike('%' + search_text + '%'))
    if service_id:
        db_vehicle = db_vehicle.filter(models.ServiceVehicles.service_id == service_id)
    db_vehicle = db_vehicle.order_by(models.VehicleStatus.update_ts)
    return db_vehicle.all()


def search_vehicle_active_by_driver(db: Session, search_text, driver_id):
    db_vehicle = vehicle_view_sample(db) \
        .filter(models.Vehicles.driver_id == driver_id) \
        .filter(models.Vehicles.state == models.EntityState.active) \
        .filter(func.array_to_string(models.Vehicles.search_meta, ',').ilike('%' + search_text + '%')) \
        .order_by(models.Vehicles.vehicle_no)
    return db_vehicle.all()


def generate_search_meta(db: Session, id, vehicle_name, vehicle_year, vehicle_color, engine_no, body_no, document_no):
    data = []
    if vehicle_name is not None:
        data.append(vehicle_name.lower())
    if vehicle_year is not None:
        data.append(str(vehicle_year).lower())
    if vehicle_color is not None:
        data.append(vehicle_color.lower())
    if engine_no is not None:
        data.append(engine_no.lower())
    if body_no is not None:
        data.append(body_no.lower())
    if document_no is not None:
        data.append(document_no.lower())
    db_vehicle = db.query(models.Vehicles).filter(models.Vehicles.id == id)
    edit_vehicle_crud = {
        models.Vehicles.search_meta: data
    }
    db_vehicle.update(edit_vehicle_crud)
    return True


# endregion


# region Vehicle Status
def add_vehicle_status(db: Session, driver_id, vehicle_id, service_ids, district_id):
    db_vehicle_status = models.VehicleStatus(id=uuid.uuid4(),
                                             driver_id=driver_id,
                                             vehicle_id=vehicle_id,
                                             service_ids=service_ids,
                                             district_id=district_id,
                                             vehicle_available=models.VehicleAvailable.free,
                                             vehicle_state=models.VehicleState.active,
                                             state=models.EntityState.active,
                                             create_ts=datetime.now(),
                                             update_ts=datetime.now())
    db.add(db_vehicle_status)
    return db_vehicle_status.id


def edit_vehicle_status(db: Session, driver_id, vehicle_id, service_ids, district_id, vehicle_available,
                        vehicle_state):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.driver_id == driver_id) \
        .filter(models.VehicleStatus.vehicle_id == vehicle_id) \
        .filter(models.VehicleStatus.state == models.EntityState.active)
    edit_vehicle_status_crud = {
        models.VehicleStatus.service_ids: service_ids,
        models.VehicleStatus.district_id: district_id,
        models.VehicleStatus.vehicle_available: vehicle_available,
        models.VehicleStatus.vehicle_state: vehicle_state,
        models.VehicleStatus.update_ts: datetime.now()
    }
    db_vehicle_status.update(edit_vehicle_status_crud)
    return True


def edit_vehicle_status_by_id(db: Session, id, service_ids, district_id, vehicle_available, vehicle_state):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.id == id)
    edit_vehicle_status_crud = {
        models.VehicleStatus.service_ids: service_ids,
        models.VehicleStatus.district_id: district_id,
        models.VehicleStatus.vehicle_available: vehicle_available,
        models.VehicleStatus.vehicle_state: vehicle_state,
        models.VehicleStatus.update_ts: datetime.now()
    }
    db_vehicle_status.update(edit_vehicle_status_crud)
    return True


def edit_vehicle_status_district(db: Session, driver_id, vehicle_id, district_id):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.driver_id == driver_id) \
        .filter(models.VehicleStatus.vehicle_id == vehicle_id) \
        .filter(models.VehicleStatus.state == models.EntityState.active)
    edit_vehicle_status_crud = {
        models.VehicleStatus.district_id: district_id,
        models.VehicleStatus.update_ts: datetime.now()
    }
    db_vehicle_status.update(edit_vehicle_status_crud)
    return True


def change_vehicle_status_available(db: Session, driver_id, vehicle_id, vehicle_available):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.driver_id == driver_id) \
        .filter(models.VehicleStatus.vehicle_id == vehicle_id) \
        .filter(models.VehicleStatus.state == models.EntityState.active)
    edit_vehicle_status_crud = {
        models.VehicleStatus.vehicle_available: vehicle_available,
        models.VehicleStatus.update_ts: datetime.now()
    }
    db_vehicle_status.update(edit_vehicle_status_crud)
    return True


def change_vehicle_status_state(db: Session, driver_id, vehicle_id, vehicle_state):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.driver_id == driver_id) \
        .filter(models.VehicleStatus.vehicle_id == vehicle_id) \
        .filter(models.VehicleStatus.state == models.EntityState.active)
    edit_vehicle_status_crud = {
        models.VehicleStatus.vehicle_state: vehicle_state,
        models.VehicleStatus.update_ts: datetime.now()
    }
    db_vehicle_status.update(edit_vehicle_status_crud)
    return True


def change_vehicle_status_available_state(db: Session, driver_id, vehicle_id, vehicle_available, vehicle_state):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.driver_id == driver_id) \
        .filter(models.VehicleStatus.vehicle_id == vehicle_id) \
        .filter(models.VehicleStatus.state == models.EntityState.active)
    edit_vehicle_status_crud = {
        models.VehicleStatus.vehicle_available: vehicle_available,
        models.VehicleStatus.vehicle_state: vehicle_state,
        models.VehicleStatus.update_ts: datetime.now()
    }
    db_vehicle_status.update(edit_vehicle_status_crud)
    return True


def get_vehicle_status_by_id(db: Session, id):
    db_vehicle_status = db.query(models.VehicleStatus).get(id)
    return db_vehicle_status


def get_vehicle_status_by_info(db: Session, driver_id, vehicle_id):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.driver_id == driver_id) \
        .filter(models.VehicleStatus.vehicle_id == vehicle_id) \
        .filter(models.VehicleStatus.state == models.EntityState.active)
    return db_vehicle_status.first()


def get_vehicle_status_by_info_minimum(db: Session, driver_id, vehicle_id):
    db_vehicle_status = vehicle_status_view_sample(db) \
        .filter(models.VehicleStatus.driver_id == driver_id) \
        .filter(models.VehicleStatus.vehicle_id == vehicle_id) \
        .filter(models.CustomerBalances.current_balance > 10) \
        .filter(models.VehicleStatus.state == models.EntityState.active)
    return db_vehicle_status.first()


def get_vehicle_status_by_info_available(db: Session, driver_id, vehicle_id):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.driver_id == driver_id) \
        .filter(models.VehicleStatus.vehicle_id == vehicle_id) \
        .filter(models.VehicleStatus.vehicle_available == models.VehicleAvailable.free) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.VehicleStatus.state == models.EntityState.active)
    return db_vehicle_status.first()


def get_vehicle_status_free_by_district(db: Session, service_id, district_id, canceled_vehicles):
    db_vehicle_status = vehicle_status_view_driver(db, district_id) \
        .filter(models.VehicleStatus.service_ids.any(service_id)) \
        .filter(models.VehicleStatus.vehicle_available == models.VehicleAvailable.free) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.VehicleStatus.state == models.EntityState.active) \
        .filter(models.VehicleStatus.vehicle_id.notin_(canceled_vehicles)) \
        .filter(models.CustomerBalances.current_balance > 10) \
        .order_by(models.VehicleStatus.update_ts)
    return db_vehicle_status.first()


def get_vehicle_status_free(db: Session, service_id, canceled_vehicles):
    db_vehicle_status = vehicle_status_view_sample(db) \
        .filter(models.VehicleStatus.service_ids.any(service_id)) \
        .filter(models.VehicleStatus.vehicle_available == models.VehicleAvailable.free) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.VehicleStatus.state == models.EntityState.active) \
        .filter(models.VehicleStatus.vehicle_id.notin_(canceled_vehicles)) \
        .filter(models.CustomerBalances.current_balance > 10) \
        .order_by(models.VehicleStatus.update_ts)
    return db_vehicle_status.first()


def get_vehicle_status_free_simple(db: Session, driver_id, vehicle_id):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.driver_id == driver_id) \
        .filter(models.VehicleStatus.vehicle_id == vehicle_id) \
        .filter(models.VehicleStatus.vehicle_available == models.VehicleAvailable.free) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.VehicleStatus.state == models.EntityState.active) \
        .order_by(models.VehicleStatus.update_ts)
    return db_vehicle_status.first()


def get_vehicle_status_list(db: Session):
    db_vehicle_status = db.query(models.VehicleStatus)
    return db_vehicle_status.all()


def get_vehicle_status_active_list(db: Session):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active)
    return db_vehicle_status.all()


def get_vehicle_status_active_list_view(db: Session):
    db_vehicle_status = db.query(models.VehicleStatus.id,
                                 models.VehicleStatus.driver_id,
                                 models.VehicleStatus.vehicle_id,
                                 models.VehicleStatus.service_ids,
                                 models.VehicleStatus.district_id,
                                 models.VehicleStatus.vehicle_available,
                                 models.VehicleStatus.vehicle_state,
                                 models.VehicleStatus.state,
                                 models.VehicleStatus.create_ts,
                                 models.VehicleStatus.update_ts,
                                 models.DriverVehicleLocation.order_id,
                                 models.DriverVehicleLocation.geo_location,
                                 models.Vehicles.vehicle_name,
                                 models.Customers.fullname) \
        .join(models.DriverVehicleLocation,
              and_(models.DriverVehicleLocation.driver_id == models.VehicleStatus.driver_id,
                   models.DriverVehicleLocation.vehicle_id == models.VehicleStatus.vehicle_id,
                   models.DriverVehicleLocation.geo_location != None)) \
        .join(models.Vehicles, models.Vehicles.id == models.VehicleStatus.vehicle_id) \
        .join(models.Customers, models.Customers.id == models.VehicleStatus.driver_id) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .distinct(models.DriverVehicleLocation.driver_id,
                  models.DriverVehicleLocation.vehicle_id) \
        .order_by(models.DriverVehicleLocation.driver_id,
                  models.DriverVehicleLocation.vehicle_id,
                  models.DriverVehicleLocation.create_ts.desc())
    return db_vehicle_status.all()


def get_vehicle_status_active_list_free_by_district(db: Session, service_id, district_id):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.service_ids.any(service_id)) \
        .filter(models.VehicleStatus.district_id == district_id) \
        .filter(models.VehicleStatus.vehicle_available == models.VehicleAvailable.free) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.VehicleStatus.state == models.EntityState.active) \
        .order_by(models.VehicleStatus.update_ts)
    return db_vehicle_status.all()


def get_vehicle_status_active_list_free(db: Session, service_id):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.service_ids.any(service_id)) \
        .filter(models.VehicleStatus.vehicle_available == models.VehicleAvailable.free) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.VehicleStatus.state == models.EntityState.active) \
        .order_by(models.VehicleStatus.update_ts)
    return db_vehicle_status.all()


def count_vehicles_active(db: Session):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.VehicleStatus.state == models.EntityState.active)
    return db_vehicle_status.count()


def count_vehicles_free(db: Session):
    db_vehicle_status = db.query(models.VehicleStatus) \
        .filter(models.VehicleStatus.vehicle_available == models.VehicleAvailable.free) \
        .filter(models.VehicleStatus.vehicle_state == models.VehicleState.active) \
        .filter(models.VehicleStatus.state == models.EntityState.active)
    return db_vehicle_status.count()


# endregion


# region Driver Vehicle Location
def add_driver_vehicle_location(db: Session, driver_id, vehicle_id, order_id, geo_location, district_id):
    db_driver_vehicle_location = models.DriverVehicleLocation(id=uuid.uuid4(),
                                                              driver_id=driver_id,
                                                              vehicle_id=vehicle_id,
                                                              order_id=order_id,
                                                              geo_location=geo_location,
                                                              district_id=district_id,
                                                              create_ts=datetime.now())
    db.add(db_driver_vehicle_location)
    return db_driver_vehicle_location.id


def get_driver_vehicle_location_last_by_info(db: Session, driver_id, vehicle_id):
    db_driver_vehicle_location = db.query(models.DriverVehicleLocation) \
        .filter(models.DriverVehicleLocation.driver_id == driver_id) \
        .filter(models.DriverVehicleLocation.vehicle_id == vehicle_id) \
        .order_by(models.DriverVehicleLocation.create_ts.desc())
    return db_driver_vehicle_location.first()


def get_driver_vehicle_location_list(db: Session):
    db_driver_vehicle_location = db.query(models.DriverVehicleLocation)
    return db_driver_vehicle_location.all()


def get_driver_vehicle_location_list_by_order(db: Session, order_id):
    db_driver_vehicle_location = db.query(models.DriverVehicleLocation) \
        .filter(models.DriverVehicleLocation.order_id == order_id) \
        .order_by(models.DriverVehicleLocation.create_ts)
    return db_driver_vehicle_location.all()


def get_driver_vehicle_location_list_by_driver(db: Session, driver_id):
    db_driver_vehicle_location = db.query(models.DriverVehicleLocation) \
        .filter(models.DriverVehicleLocation.driver_id == driver_id) \
        .order_by(models.DriverVehicleLocation.create_ts)
    return db_driver_vehicle_location.all()

# endregion
