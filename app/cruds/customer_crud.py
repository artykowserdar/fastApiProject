import datetime
import json
import uuid
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app import models


# region Samples to use
def customer_view_sample(db: Session):
    join_query = db.query(models.Customers.id,
                          models.Customers.code,
                          models.Customers.fullname,
                          models.Customers.initials,
                          models.Customers.address,
                          models.Customers.birth_date,
                          models.Customers.birth_place,
                          models.Customers.gender,
                          models.Customers.customer_type,
                          models.Customers.discount_percent,
                          models.Customers.discount_limit,
                          models.Customers.phone,
                          models.Customers.employee_type,
                          models.Customers.username,
                          models.Customers.image_name,
                          models.Customers.image_path,
                          models.Customers.blacklist,
                          models.Customers.rating,
                          models.Customers.state,
                          models.Customers.create_ts,
                          models.Customers.update_ts,
                          models.CustomerBalances.current_balance) \
        .outerjoin(models.CustomerBalances, models.CustomerBalances.customer_id == models.Customers.id)
    return join_query


def customer_rating_view_sample(db: Session):
    join_query = db.query(models.CustomerRatings.id,
                          models.CustomerRatings.set_customer_id,
                          models.CustomerRatings.get_customer_id,
                          models.CustomerRatings.rating,
                          models.CustomerRatings.comment,
                          models.CustomerRatings.state,
                          models.CustomerRatings.create_ts,
                          models.CustomerRatings.update_ts,
                          models.Customers.fullname) \
        .outerjoin(models.Customers, models.Customers.id == models.CustomerRatings.set_customer_id)
    return join_query


# endregion


# region Customer
def add_customer(db: Session, fullname, initials, address, birth_date, birth_place, gender, customer_type, code,
                 discount_percent, discount_limit, card_no, phone, username, employee_type, image_name, image_path,
                 action_user):
    db_customer = models.Customers(id=uuid.uuid4(),
                                   code=code,
                                   fullname=fullname,
                                   initials=initials,
                                   address=address,
                                   birth_date=birth_date,
                                   birth_place=birth_place,
                                   gender=gender,
                                   customer_type=customer_type,
                                   discount_percent=discount_percent,
                                   discount_limit=discount_limit,
                                   card_no=card_no,
                                   phone=phone,
                                   username=username,
                                   employee_type=employee_type,
                                   image_name=image_name,
                                   image_path=image_path,
                                   state=models.EntityState.active.name,
                                   create_ts=datetime.now(),
                                   update_ts=datetime.now())
    db.add(db_customer)
    db.flush()
    generate_search_meta(db, db_customer.id, fullname, phone)
    add_customer_balance(db, db_customer.id, 0, action_user)
    if action_user:
        customer_json_info = {'code': str(code),
                              'fullname': str(fullname),
                              'address': str(address),
                              'birth_date': str(birth_date),
                              'birth_place': str(birth_place),
                              'gender': str(gender),
                              'customer_type': str(customer_type),
                              'discount_percent': str(discount_percent),
                              'discount_limit': str(discount_limit),
                              'card_no': str(card_no),
                              'phone': str(phone)}
        db_customer_log = models.CustomerLog(id=uuid.uuid4(),
                                             customer_id=db_customer.id,
                                             action=models.CustomerAction.CustomerAdd,
                                             action_user=action_user,
                                             sup_info=json.dumps(customer_json_info),
                                             action_ts=datetime.now())
        db.add(db_customer_log)
    return db_customer.id


def add_customer_blacklist(db: Session, id, blacklist, action_user):
    db_customer = db.query(models.Customers).filter(models.Customers.id == id)
    edit_customer_crud = {
        models.Customers.blacklist: blacklist,
        models.Customers.update_ts: datetime.now()
    }
    db_customer.update(edit_customer_crud)
    customer_json_info = {'blacklist': str(blacklist)}
    db_customer_log = models.CustomerLog(id=uuid.uuid4(),
                                         customer_id=id,
                                         action=models.CustomerAction.CustomerAddBlacklist,
                                         action_user=action_user,
                                         sup_info=json.dumps(customer_json_info),
                                         action_ts=datetime.now())
    db.add(db_customer_log)
    return id


def add_user_to_customer(db: Session, id, username, action_user):
    db_customer = db.query(models.Customers).filter(models.Customers.id == id)
    edit_customer_crud = {
        models.Customers.username: username,
        models.Customers.update_ts: datetime.now()
    }
    db_customer.update(edit_customer_crud)
    if action_user:
        customer_json_info = {'username': str(username)}
        db_customer_log = models.CustomerLog(id=uuid.uuid4(),
                                             customer_id=id,
                                             action=models.CustomerAction.CustomerEdit,
                                             action_user=action_user,
                                             sup_info=json.dumps(customer_json_info),
                                             action_ts=datetime.now())
        db.add(db_customer_log)
    return id


def edit_customer(db: Session, id, fullname, initials, address, birth_date, birth_place, gender, customer_type,
                  discount_percent, discount_limit, card_no, phone, employee_type, image_name, image_path, action_user):
    db_customer = db.query(models.Customers).filter(models.Customers.id == id)
    edit_customer_crud = {
        models.Customers.fullname: fullname,
        models.Customers.initials: initials,
        models.Customers.address: address,
        models.Customers.birth_date: birth_date,
        models.Customers.birth_place: birth_place,
        models.Customers.gender: gender,
        models.Customers.customer_type: customer_type,
        models.Customers.discount_percent: discount_percent or 0,
        models.Customers.discount_limit: discount_limit or 0,
        models.Customers.card_no: card_no,
        models.Customers.phone: phone,
        models.Customers.employee_type: employee_type,
        models.Customers.image_name: image_name,
        models.Customers.image_path: image_path,
        models.Customers.update_ts: datetime.now()
    }
    db_customer.update(edit_customer_crud)
    generate_search_meta(db, id, fullname, phone)
    customer_json_info = {'fullname': str(fullname),
                          'address': str(address),
                          'birth_date': str(birth_date),
                          'birth_place': str(birth_place),
                          'gender': str(gender),
                          'customer_type': str(customer_type),
                          'discount_percent': str(discount_percent),
                          'discount_limit': str(discount_limit),
                          'card_no': str(card_no),
                          'phone': str(phone)}
    db_customer_log = models.CustomerLog(id=uuid.uuid4(),
                                         customer_id=id,
                                         action=models.CustomerAction.CustomerEdit,
                                         action_user=action_user,
                                         sup_info=json.dumps(customer_json_info),
                                         action_ts=datetime.now())
    db.add(db_customer_log)
    return id


def edit_customer_rating_data(db: Session, id, rating):
    db_customer = db.query(models.Customers).filter(models.Customers.id == id)
    edit_customer_crud = {
        models.Customers.rating: rating,
        models.Customers.update_ts: datetime.now()
    }
    db_customer.update(edit_customer_crud)
    return id


def change_customer_state(db: Session, id, state, action_user):
    db_customer = db.query(models.Customers).filter(models.Customers.id == id)
    edit_customer_crud = {
        models.Customers.state: state,
        models.Customers.update_ts: datetime.now()
    }
    db_customer.update(edit_customer_crud)
    change_customer_balance_state(db, id, state, action_user)
    customer_json_info = {'state': state.name}
    db_customer_log = models.CustomerLog(id=uuid.uuid4(),
                                         customer_id=id,
                                         action=models.CustomerAction.CustomerStateChange,
                                         action_user=action_user,
                                         sup_info=json.dumps(customer_json_info),
                                         action_ts=datetime.now())
    db.add(db_customer_log)
    return id


def get_customer_by_id(db: Session, id):
    db_customer = customer_view_sample(db) \
        .filter(models.Customers.id == id).first()
    return db_customer


def get_customer_by_id_sample(db: Session, id):
    db_customer = db.query(models.Customers).get(id)
    return db_customer


def get_customer_by_phone(db: Session, phone):
    db_customer = db.query(models.Customers) \
        .filter(models.Customers.phone == phone).first()
    return db_customer


def get_customer_by_phone_no_id(db: Session, id, phone):
    db_customer = db.query(models.Customers) \
        .filter(models.Customers.id != id) \
        .filter(models.Customers.phone == phone).first()
    return db_customer


def get_customer_by_username(db: Session, username):
    db_customer = customer_view_sample(db) \
        .filter(models.Customers.username == username).first()
    return db_customer


def get_customer_by_username_minimum(db: Session, username):
    db_customer = customer_view_sample(db) \
        .filter(models.Customers.username == username) \
        .filter(models.CustomerBalances.current_balance > 10).first()
    return db_customer


def get_customer_list_simple(db: Session):
    db_customer = db.query(models.Customers)
    return db_customer.all()


def get_customer_active_list(db: Session):
    db_customer = customer_view_sample(db) \
        .filter(models.Customers.state == models.EntityState.active) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def get_customer_active_list_by_type(db: Session, customer_type):
    db_customer = customer_view_sample(db) \
        .filter(models.Customers.customer_type == customer_type) \
        .filter(models.Customers.state == models.EntityState.active) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def get_customer_active_list_by_type_sample(db: Session, customer_type):
    db_customer = db.query(models.Customers) \
        .filter(models.Customers.customer_type == customer_type) \
        .filter(models.Customers.state == models.EntityState.active)
    return db_customer.all()


def get_customer_active_list_employee(db: Session):
    db_customer = db.query(models.Customers) \
        .filter(models.Customers.customer_type == models.CustomerType.employee) \
        .filter(models.Customers.state == models.EntityState.active) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def get_customer_active_list_employee_driver(db: Session):
    db_customer = db.query(models.Customers) \
        .filter(models.Customers.customer_type == models.CustomerType.employee) \
        .filter(models.Customers.employee_type == models.EmployeeType.driver) \
        .filter(models.Customers.state == models.EntityState.active) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def get_customer_active_list_employee_boss(db: Session):
    db_customer = db.query(models.Customers) \
        .filter(models.Customers.customer_type == models.CustomerType.employee) \
        .filter(or_(models.Customers.employee_type == models.EmployeeType.admin,
                    models.Customers.employee_type == models.EmployeeType.boss)) \
        .filter(models.Customers.state == models.EntityState.active) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def get_customer_active_list_by_type_not_blacklist(db: Session, customer_type):
    db_customer = customer_view_sample(db) \
        .filter(models.Customers.customer_type == customer_type) \
        .filter(models.Customers.blacklist == False) \
        .filter(models.Customers.state == models.EntityState.active) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def get_customer_active_list_not_assigned(db: Session):
    db_customer = customer_view_sample(db) \
        .filter(models.Customers.customer_type == models.CustomerType.employee) \
        .filter(models.Customers.username == None) \
        .filter(models.Customers.state == models.EntityState.active) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def get_customer_active_list_not_assigned_user(db: Session, username):
    db_customer = customer_view_sample(db) \
        .filter(models.Customers.customer_type == models.CustomerType.employee) \
        .filter(or_(models.Customers.username == None,
                    models.Customers.username != username)) \
        .filter(models.Customers.state == models.EntityState.active) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def get_customer_active_list_by_employee_type(db: Session, employee_type):
    db_customer = customer_view_sample(db) \
        .filter(models.Customers.employee_type == employee_type) \
        .filter(models.Customers.state == models.EntityState.active) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def get_customer_active_list_by_employee_sample(db: Session, employee_type):
    db_customer = db.query(models.Customers) \
        .filter(models.Customers.employee_type == employee_type) \
        .filter(models.Customers.state == models.EntityState.active)
    return db_customer.all()


def search(db: Session, search_text):
    db_customer = customer_view_sample(db) \
        .filter(func.array_to_string(models.Customers.search_meta, ',').ilike('%' + search_text + '%')) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def search_active(db: Session, search_text):
    db_customer = customer_view_sample(db) \
        .filter(models.Customers.state == models.EntityState.active) \
        .filter(func.array_to_string(models.Customers.search_meta, ',').ilike('%' + search_text + '%')) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def search_active_by_type(db: Session, search_text, customer_type):
    db_customer = customer_view_sample(db) \
        .filter(models.Customers.state == models.EntityState.active) \
        .filter(models.Customers.customer_type == customer_type) \
        .filter(func.array_to_string(models.Customers.search_meta, ',').ilike('%' + search_text + '%')) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def search_active_by_employee_type(db: Session, search_text, employee_type):
    db_customer = customer_view_sample(db) \
        .filter(models.Customers.state == models.EntityState.active) \
        .filter(models.Customers.customer_type == models.CustomerType.employee)
    if employee_type:
        db_customer = db_customer.filter(models.Customers.employee_type == employee_type)
    db_customer = db_customer.filter(
        func.array_to_string(models.Customers.search_meta, ',').ilike('%' + search_text + '%')) \
        .order_by(models.Customers.fullname)
    return db_customer.all()


def generate_search_meta(db: Session, id, fullname, phone):
    data = []
    if fullname is not None:
        data.append(fullname.lower())
    if phone is not None:
        data.append(phone.lower())

    db_customer = db.query(models.Customers).filter(models.Customers.id == id)
    edit_customer_crud = {
        models.Customers.search_meta: data,
        models.Customers.update_ts: datetime.now()
    }
    db_customer.update(edit_customer_crud)
    return True


# endregion


# region Customer Balances
def add_customer_balance(db: Session, customer_id, current_balance, action_user):
    db_customer_balance = models.CustomerBalances(id=uuid.uuid4(),
                                                  customer_id=customer_id,
                                                  current_balance=current_balance,
                                                  state=models.EntityState.active.name,
                                                  create_ts=datetime.now(),
                                                  update_ts=datetime.now())
    db.add(db_customer_balance)
    db.flush()
    if action_user:
        customer_balance_json_info = {'customer_id': str(customer_id),
                                      'current_balance': current_balance}
        db_customer_balance_log = models.CustomerBalanceLog(id=uuid.uuid4(),
                                                            customer_balance_id=db_customer_balance.id,
                                                            action=models.CustomerBalanceAction.CustomerBalanceAdd,
                                                            action_user=action_user,
                                                            sup_info=json.dumps(customer_balance_json_info),
                                                            action_ts=datetime.now())
        db.add(db_customer_balance_log)
    return db_customer_balance.id


def edit_customer_balance(db: Session, id, current_balance, action_user):
    db_customer_balance = db.query(models.CustomerBalances).filter(models.CustomerBalances.id == id)
    edit_customer_balance_crud = {
        models.CustomerBalances.current_balance: current_balance,
        models.CustomerBalances.update_ts: datetime.now()
    }
    db_customer_balance.update(edit_customer_balance_crud)
    customer_balance_json_info = {'current_balance': current_balance}
    db_customer_balance_log = models.CustomerBalanceLog(id=uuid.uuid4(),
                                                        customer_balance_id=id,
                                                        action=models.CustomerBalanceAction.CustomerBalanceEdit,
                                                        action_user=action_user,
                                                        sup_info=json.dumps(customer_balance_json_info),
                                                        action_ts=datetime.now())
    db.add(db_customer_balance_log)
    return id


def change_customer_balance_state(db: Session, customer_id, state, action_user):
    db_customer_balance = db.query(models.CustomerBalances) \
        .filter(models.CustomerBalances.customer_id == customer_id).first()
    id = db_customer_balance.id
    db_customer_balance = db.query(models.CustomerBalances).filter(models.CustomerBalances.id == id)
    edit_customer_balance_crud = {
        models.CustomerBalances.state: state,
        models.CustomerBalances.update_ts: datetime.now()
    }
    db_customer_balance.update(edit_customer_balance_crud)
    customer_balance_json_info = {'state': state.name}
    db_customer_balance_log = models.CustomerBalanceLog(id=uuid.uuid4(),
                                                        customer_balance_id=id,
                                                        action=models.CustomerBalanceAction.CustomerBalanceStateChange,
                                                        action_user=action_user,
                                                        sup_info=json.dumps(customer_balance_json_info),
                                                        action_ts=datetime.now())
    db.add(db_customer_balance_log)
    return id


def get_customer_balance_by_customer(db: Session, customer_id):
    db_customer_balance = db.query(models.CustomerBalances) \
        .filter(models.CustomerBalances.customer_id == customer_id).first()
    return db_customer_balance


def get_customer_balance_by_customer_minimum(db: Session, customer_id):
    db_customer_balance = db.query(models.CustomerBalances) \
        .filter(models.CustomerBalances.customer_id == customer_id) \
        .filter(models.CustomerBalances.current_balance > 10).first()
    return db_customer_balance


def get_all_customer_balance_sum(db: Session):
    db_customer_balance = db.query(func.sum(models.CustomerBalances.current_balance).label("current_balance")) \
        .join(models.Customers, models.Customers.id == models.CustomerBalances.customer_id).first()
    return db_customer_balance


def get_all_customer_balance_sum_type(db: Session, customer_type):
    db_customer_balance = db.query(func.sum(models.CustomerBalances.current_balance).label("current_balance")) \
        .join(models.Customers, models.Customers.id == models.CustomerBalances.customer_id) \
        .filter(models.Customers.customer_type == customer_type).first()
    return db_customer_balance


def get_all_client_balance_sum(db: Session, customer_type):
    db_customer_balance = db.query(func.sum(models.CustomerBalances.current_balance).label("current_balance")) \
        .join(models.Customers, models.Customers.id == models.CustomerBalances.customer_id)
    if customer_type:
        db_customer_balance = db_customer_balance.filter(models.Customers.customer_type == customer_type)
    return db_customer_balance.first()


# endregion


# region Client Address History
def add_client_address_history(db: Session, client_id, district_id, address_type, address, coordinates):
    db_client_address_history = models.ClientAddressHistory(id=uuid.uuid4(),
                                                            client_id=client_id,
                                                            district_id=district_id,
                                                            address_type=address_type,
                                                            address=address,
                                                            coordinates=coordinates,
                                                            state=models.EntityState.active.name,
                                                            create_ts=datetime.now(),
                                                            update_ts=datetime.now())
    db.add(db_client_address_history)
    return db_client_address_history.id


def change_client_address_history_state(db: Session, id, state):
    db_client_address_history = db.query(models.ClientAddressHistory) \
        .filter(models.ClientAddressHistory.id == id)
    edit_client_address_history_crud = {
        models.ClientAddressHistory.state: state,
        models.ClientAddressHistory.update_ts: datetime.now()
    }
    db_client_address_history.update(edit_client_address_history_crud)
    return id


def update_client_address_history(db: Session, id):
    db_client_address_history = db.query(models.ClientAddressHistory) \
        .filter(models.ClientAddressHistory.id == id)
    edit_client_address_history_crud = {
        models.ClientAddressHistory.update_ts: datetime.now()
    }
    db_client_address_history.update(edit_client_address_history_crud)
    return id


def get_client_address_history_by_address(db: Session, client_id, address_type, address):
    db_client_address_history = db.query(models.ClientAddressHistory) \
        .filter(models.ClientAddressHistory.client_id == client_id) \
        .filter(models.ClientAddressHistory.address_type == address_type) \
        .filter(models.ClientAddressHistory.address == address).first()
    return db_client_address_history


def get_client_address_history_by_coordinates(db: Session, client_id, address_type, coordinates):
    db_client_address_history = db.query(models.ClientAddressHistory) \
        .filter(models.ClientAddressHistory.client_id == client_id) \
        .filter(models.ClientAddressHistory.address_type == address_type) \
        .filter(models.ClientAddressHistory.coordinates == coordinates).first()
    return db_client_address_history


def get_client_address_history_list(db: Session):
    db_client_address_history = db.query(models.ClientAddressHistory)
    return db_client_address_history.all()


def get_client_address_history_active_list(db: Session):
    db_client_address_history = db.query(models.ClientAddressHistory) \
        .filter(models.ClientAddressHistory.state == models.EntityState.active)
    return db_client_address_history.all()


def get_client_address_history_active_list_by_client(db: Session, client_id):
    db_client_address_history = db.query(models.ClientAddressHistory) \
        .filter(models.ClientAddressHistory.client_id == client_id) \
        .filter(models.ClientAddressHistory.state == models.EntityState.active) \
        .order_by(models.ClientAddressHistory.update_ts.desc())
    return db_client_address_history.limit(10).all()


def get_client_address_history_active_list_by_client_type(db: Session, client_id, address_type):
    db_client_address_history = db.query(models.ClientAddressHistory) \
        .filter(models.ClientAddressHistory.client_id == client_id) \
        .filter(models.ClientAddressHistory.address_type == address_type) \
        .filter(models.ClientAddressHistory.state == models.EntityState.active) \
        .order_by(models.ClientAddressHistory.update_ts.desc())
    return db_client_address_history.limit(5).all()


def get_client_address_history_active_list_by_type_order(db: Session, client_id, address_type):
    db_client_address_history = db.query(models.ClientAddressHistory) \
        .filter(models.ClientAddressHistory.client_id == client_id) \
        .filter(models.ClientAddressHistory.address_type == address_type) \
        .filter(models.ClientAddressHistory.state == models.EntityState.active) \
        .order_by(models.ClientAddressHistory.update_ts.desc())
    return db_client_address_history.limit(5).all()


def search_active_client_address_history_by_client_type(db: Session, search_text, client_id, address_type):
    db_client_address_history = db.query(models.ClientAddressHistory) \
        .filter(models.ClientAddressHistory.client_id == client_id) \
        .filter(models.ClientAddressHistory.state == models.EntityState.active)
    if address_type:
        db_client_address_history = db_client_address_history \
            .filter(models.ClientAddressHistory.address_type == address_type)
    db_client_address_history = db_client_address_history \
        .filter(models.ClientAddressHistory.address.ilike('%' + search_text + '%')) \
        .order_by(models.ClientAddressHistory.update_ts.desc())
    return db_client_address_history.all()


# endregion


# region Customer Ratings
def add_customer_rating(db: Session, set_customer_id, get_customer_id, rating, comment):
    db_customer_rating = models.CustomerRatings(id=uuid.uuid4(),
                                                set_customer_id=set_customer_id,
                                                get_customer_id=get_customer_id,
                                                rating=rating,
                                                comment=comment,
                                                state=models.EntityState.active,
                                                create_ts=datetime.now(),
                                                update_ts=datetime.now())
    db.add(db_customer_rating)
    return db_customer_rating.id


def edit_customer_rating(db: Session, id, rating, comment):
    db_customer_rating = db.query(models.CustomerRatings) \
        .filter(models.CustomerRatings.id == id)
    edit_customer_rating_crud = {
        models.CustomerRatings.rating: rating,
        models.CustomerRatings.comment: comment,
        models.CustomerRatings.update_ts: datetime.now()
    }
    db_customer_rating.update(edit_customer_rating_crud)
    return id


def update_customer_rating_state(db: Session, id, rating, comment, state):
    db_customer_rating = db.query(models.CustomerRatings) \
        .filter(models.CustomerRatings.id == id)
    edit_customer_rating_crud = {
        models.CustomerRatings.rating: rating,
        models.CustomerRatings.comment: comment,
        models.CustomerRatings.state: state,
        models.CustomerRatings.update_ts: datetime.now()
    }
    db_customer_rating.update(edit_customer_rating_crud)
    return id


def change_customer_rating_state(db: Session, id, state):
    db_customer_rating = db.query(models.CustomerRatings) \
        .filter(models.CustomerRatings.id == id)
    edit_customer_rating_crud = {
        models.CustomerRatings.state: state,
        models.CustomerRatings.update_ts: datetime.now()
    }
    db_customer_rating.update(edit_customer_rating_crud)
    return id


def get_customer_rating_by_id(db: Session, id):
    db_customer_rating = db.query(models.CustomerRatings) \
        .filter(models.CustomerRatings.id == id).first()
    return db_customer_rating


def get_customer_rating_by_info(db: Session, set_customer_id, get_customer_id):
    db_customer_rating = db.query(models.CustomerRatings) \
        .filter(models.CustomerRatings.set_customer_id == set_customer_id) \
        .filter(models.CustomerRatings.get_customer_id == get_customer_id).first()
    return db_customer_rating


def get_customer_rating_active_list(db: Session):
    db_customer_rating = db.query(models.CustomerRatings) \
        .filter(models.CustomerRatings.state == models.EntityState.active)
    return db_customer_rating.all()


def get_customer_rating_active_list_by_set_customer(db: Session, set_customer_id):
    db_customer_rating = db.query(models.CustomerRatings) \
        .filter(models.CustomerRatings.set_customer_id == set_customer_id) \
        .filter(models.CustomerRatings.state == models.EntityState.active) \
        .order_by(models.CustomerRatings.update_ts.desc())
    return db_customer_rating.all()


def get_customer_rating_active_list_by_get_customer(db: Session, get_customer_id):
    db_customer_rating = db.query(models.CustomerRatings) \
        .filter(models.CustomerRatings.get_customer_id == get_customer_id) \
        .filter(models.CustomerRatings.state == models.EntityState.active) \
        .order_by(models.CustomerRatings.update_ts.desc())
    return db_customer_rating.all()


def get_customer_rating_active_group_by_get_customer(db: Session, get_customer_id):
    db_customer_rating = db.query(models.CustomerRatings.get_customer_id,
                                  func.avg(models.CustomerRatings.rating).label("rating")) \
        .filter(models.CustomerRatings.get_customer_id == get_customer_id) \
        .filter(models.CustomerRatings.state == models.EntityState.active) \
        .group_by(models.CustomerRatings.get_customer_id)
    return db_customer_rating.first()


def search_customer_rating_active_by_get_customer(db: Session, get_customer_id, search_text):
    db_customer_rating = customer_rating_view_sample(db) \
        .filter(models.CustomerRatings.get_customer_id == get_customer_id) \
        .filter(func.array_to_string(models.Customers.search_meta, ',').ilike('%' + search_text + '%')) \
        .filter(models.CustomerRatings.state == models.EntityState.active) \
        .order_by(models.CustomerRatings.update_ts.desc())
    return db_customer_rating.all()


# endregion


# region Logs
def get_customer_log_list_customer_id(db: Session, customer_id):
    db_log = db.query(models.CustomerLog) \
        .filter(models.CustomerLog.customer_id == customer_id).all()
    return db_log


def get_customer_balance_log_list_customer_balance_id(db: Session, customer_balance_id):
    db_log = db.query(models.CustomerBalanceLog) \
        .filter(models.CustomerBalanceLog.customer_balance_id == customer_balance_id).all()
    return db_log
# endregion
