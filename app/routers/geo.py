import logging
from typing import List

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app import schemas
from app.accesses import geo_access, token_access
from app.database import get_db
from app.lib import get_remote_ip

router = APIRouter()
log = logging.getLogger(__name__)


# region Open Street Map
@router.post("/address-search/", response_model=List[schemas.SearchAddress])
def get_address_search(request: Request, city: str = Form(...), address: str = Form(...), lang: str = Form(...),
                       db: Session = Depends(get_db),
                       current_user: schemas.Users = Depends(token_access.get_current_active_user),
                       authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Addresses searched - %s", current_user.username, get_remote_ip(request))

    address_list = geo_access.get_address_search(db, city=city, address=address, lang=lang)

    if address_list["status"] != 200:
        log.exception(address_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=address_list["status"], detail=address_list["error_msg"])
    return address_list["result"]


@router.post("/address-search-by-coordinates/", response_model=schemas.SearchAddress)
def get_address_search_by_coordinates(request: Request, latitude: float = Form(...), longitude: float = Form(...),
                                      lang: str = Form(...), db: Session = Depends(get_db),
                                      current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Addresses searched - %s", current_user.username, get_remote_ip(request))

    address_list = geo_access.get_address_search_by_coordinates(db, latitude=latitude, longitude=longitude, lang=lang)

    if address_list["status"] != 200:
        log.exception(address_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=address_list["status"], detail=address_list["error_msg"])
    return address_list["result"]


@router.post("/distance-between-coordinates/")
def get_distance_between_coordinates(request: Request, latitude_from: float = Form(...),
                                     longitude_from: float = Form(...), latitude_to: float = Form(...),
                                     longitude_to: float = Form(...),
                                     current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                     authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Coordinates distance between - %s", current_user.username, get_remote_ip(request))

    address_list = geo_access.get_distance_between_coordinates(latitude_from=latitude_from,
                                                               longitude_from=longitude_from,
                                                               latitude_to=latitude_to,
                                                               longitude_to=longitude_to)

    if address_list["status"] != 200:
        log.exception(address_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=address_list["status"], detail=address_list["error_msg"])
    return address_list["result"]


@router.post("/distance-between-coordinates-full/")
def get_distance_between_coordinates_full(request: Request, address1: str = Form(None), address2: str = Form(...),
                                          db: Session = Depends(get_db),
                                          current_user: schemas.Users = Depends(token_access.get_current_active_user),
                                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    log.debug("%s - Coordinates distance between - %s", current_user.username, get_remote_ip(request))

    address_list = geo_access.get_distance_between_coordinates_full(db, address1=address1,
                                                                    address2=address2)

    if address_list["status"] != 200:
        log.exception(address_list["error_msg"] + ' - %s - %s', current_user.username, get_remote_ip(request))
        raise HTTPException(status_code=address_list["status"], detail=address_list["error_msg"])
    return address_list["result"]


# endregion
