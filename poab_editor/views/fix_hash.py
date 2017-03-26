from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from pyramid.security import (
    authenticated_userid,
    forget,
    remember
)


from poab_editor.models import (
    DBSession,
    Log,
    Image,
    Track,
    Author,
    ComplexEncoder
    )

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden
    )

import hashlib, json, requests
from poab_editor.helpers import (
    timetools,
    imagetools,
    filetools,
    gpxtools
    )

from time import strftime
import json
import requests


@view_config(route_name='hash_fix')
def hashfix(request):
    log = DBSession.query(Log).filter(Log.id==52).one()
    images = DBSession.query(Image).filter(Image.logs.contains(log)).order_by(Image.timestamp_original).all()
    n = 0
    for image in images:
        hash = hashlib.sha256(open(image.location+image.name).read()).hexdigest()
        if image.hash != hash:
            print('#', n)
            n=n+1
            print(image.id, image.location+image.name, image.hash)
            print(image.id, image.location+image.name, hash, '\n')
            image.hash = hash
    return Response('OK')
        
