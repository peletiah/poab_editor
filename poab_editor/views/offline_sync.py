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



@view_config(route_name='sync')
def sync(request):
    print request.json_body
    print request.json_body['image']['id']
    image = Image.get_image_by_id(request.json_body['image']['id'])
    log = request.json_body['log']
    print image
    image_bin = open(image.location+image.name, 'rb')
    url = 'http://poab.org:6543/upload'
    payload = {'metadata':json.dumps(image.reprJSON()), 'image_bin':image_bin, 'log':json.dumps(log)}
    headers = {'content-type':'application/json'}
    r = requests.post(url, files=payload)
    print r.text
    return Response(r.text)

