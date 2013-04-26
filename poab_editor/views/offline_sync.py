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


@view_config(route_name='sync', request_param='type=log')
def logsync(request):
    log_json = request.json_body['log']
    print log_json
    log = Log.get_log_by_id(log_json['id'])
    print log.id
    url = 'http://localhost:6544/sync?type=log'
    payload = {'log':json.dumps(log.reprJSON())}
    headers = {'content-type':'application/json'}
    r = requests.post(url, files=payload)
    sync_status=json.loads(r.text)['sync_status'] #if sync_status is True, we already have this image on the server
    return Response(r.text)




@view_config(route_name='sync', request_param='type=image')
def imagesync(request):
    image = Image.get_image_by_id(request.json_body['image']['id'])
    log_json = request.json_body['log']
    log = Log.get_log_by_id(log_json['id'])

    headers = {'content-type':'application/json'}
    url = 'http://localhost:6544/sync?type=status'
    payload = {'filetype':'image', 'metadata':json.dumps(image.reprJSON())}
    r = requests.post(url, data=payload)

    sync_status=json.loads(r.text)['sync_status'] #if sync_status is True, we already have this image on the server
    print '\n################ IMAGE SYNC STATUS: '+sync_status+str(log.id) + '\n'

    if sync_status == 'not_synced':
        image_bin = open(image.location+image.name, 'rb')
        url = 'http://localhost:6544/sync?type=image'
        payload = {'metadata':json.dumps(image.reprJSON_extended()), 'image_bin':image_bin, 'log':json.dumps(log.reprJSON())}
        headers = {'content-type':'application/json'}
        r = requests.post(url, files=payload)
        return Response(r.text)

    elif sync_status == 'was_synced':
        return Response(json.dumps({'item_uuid':image.uuid, 'log_id':log.id, 'sync_status':sync_status}))

    return Response(json.dumps({'item_uuid':None, 'log_id':log.id, 'sync_status':sync_status}))

@view_config(route_name='sync', request_param='type=track')
def tracksync(request):
    track = Track.get_track_by_id(request.json_body['track']['id'])
    log = request.json_body['log']
    print track.reprJSON_extended()['author']
    headers = {'content-type':'application/json'}
    url = 'http://localhost:6544/sync?type=track'
    payload = {'track':json.dumps(track.reprJSON_extended()), 'log':json.dumps(log)}
    r = requests.post(url, data=payload)

    return Response(r.text)

