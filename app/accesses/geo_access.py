import logging
import math

from geoalchemy2.shape import to_shape
from shapely import wkt
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from shapely.geometry import Point, Polygon
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import FlushError

from app.accesses import temp_access
from app.cruds import vehicle_crud

log = logging.getLogger(__name__)
api_key = "49acc7e9-3088-4a0b-8ddc-810d0ec6dcea"


# region Open Street Map
def get_address_search(db: Session, city, address, lang):
    try:
        status = 200
        error_msg = ''
        response = []
        db_district = temp_access.get_district_active_list(db)
        # Initialize Nominatim geocoder
        geolocator = Nominatim(user_agent="taxi_backend")

        # Concatenate the address and city with a comma
        query = f"{address}, {city}"

        # Perform the geocode request
        db_location = geolocator.geocode(query, addressdetails=True, namedetails=True, language=lang, limit=10,
                                         exactly_one=False, timeout=30)
        if db_location:
            for location in db_location:
                latitude = location.latitude
                longitude = location.longitude
                address = location.address
                point = (latitude, longitude)
                point = Point(point)
                district_id = None
                for district in db_district["result"]:
                    polygon = Polygon(district["district_geo"])
                    if polygon.contains(point):
                        district_id = district["id"]
                response.append({"latitude": latitude,
                                 "longitude": longitude,
                                 "address": address,
                                 "district_id": district_id})
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        response = None
        error_msg = 'get_address_search_error'
    return {"status": status, "error_msg": error_msg, "result": response}


def get_address_search_by_coordinates(db: Session, latitude, longitude, lang):
    try:
        status = 200
        error_msg = ''
        response = None
        db_district = temp_access.get_district_active_list(db)
        # Initialize Nominatim geocoder
        geolocator = Nominatim(user_agent="taxi_backend")

        coordinates = (latitude, longitude)

        # Perform the geocode request
        db_location = geolocator.reverse(coordinates, language=lang, timeout=30)
        if db_location:
            latitude = db_location.latitude
            longitude = db_location.longitude
            address = db_location.address
            point = (latitude, longitude)
            point = Point(point)
            district_id = None
            for district in db_district["result"]:
                polygon = Polygon(district["district_geo"])
                if polygon.contains(point):
                    district_id = district["id"]
            response = {"latitude": latitude,
                        "longitude": longitude,
                        "address": address,
                        "district_id": district_id}
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        response = None
        error_msg = 'get_address_search_by_coordinates_error'
    return {"status": status, "error_msg": error_msg, "result": response}


def get_district_by_coordinates(db: Session, latitude, longitude):
    try:
        status = 200
        error_msg = ''
        district_id = None
        district_name = {"tm": '', "ru": '', "en": ''}
        db_district = temp_access.get_district_active_list(db)
        # Initialize Nominatim geocoder
        geolocator = Nominatim(user_agent="taxi_backend")

        coordinates = (latitude, longitude)

        # Perform the geocode request
        db_location = geolocator.reverse(coordinates, timeout=30)
        if db_location:
            point = (latitude, longitude)
            point = Point(point)
            for district in db_district["result"]:
                polygon = Polygon(district["district_geo"])
                if polygon.contains(point):
                    district_id = district["id"]
                    district_name = district["district_name"]
        result = {"district_id": district_id,
                  "district_name": district_name}
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        result = None
        error_msg = 'get_address_search_by_coordinates_error'
    return {"status": status, "error_msg": error_msg, "result": result}


def get_distance_between_coordinates(latitude_from, longitude_from, latitude_to, longitude_to):
    try:
        status = 200
        error_msg = ''
        address1 = (latitude_from, longitude_from)
        address2 = (latitude_to, longitude_to)
        distance = geodesic(address1, address2).kilometers
        result = {"distance": distance,
                  "time": math.ceil(distance)}
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        result = None
        error_msg = 'get_address_search_by_coordinates_error'
    return {"status": status, "error_msg": error_msg, "result": result}


def get_distance_between_coordinates_full(db: Session, address1, address2):
    try:
        status = 200
        error_msg = ''
        if address1 is None:
            db_driver = (vehicle_crud
                         .get_driver_vehicle_location_last_by_info(db, "cf67ac08-eb59-4ab1-838b-d1952f81db14",
                                                                   "3cceb1e4-4339-4768-b0e3-e35222644b17"))
            geo_location = db_driver.geo_location
            shapely_geometry = to_shape(geo_location)
            wkt_representation = shapely_geometry.wkt
            point = wkt.loads(wkt_representation)
            address1 = list(point.coords[0])
        distance = geodesic(address1, address2).meters
        time = distance / 800
        result = {"distance": distance,
                  "time": math.ceil(time)}
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        status = 418
        result = None
        error_msg = 'get_address_search_by_coordinates_error'
    return {"status": status, "error_msg": error_msg, "result": result}


def get_distance_between_coordinates_full2(address1, address2):
    try:
        distance = geodesic(address1, address2).meters
        time = distance / 500
        result = {"distance": distance,
                  "time": math.ceil(time)}
    except (IntegrityError, FlushError) as exc:
        log.exception('%s', exc)
        result = None
    return result


# endregion
