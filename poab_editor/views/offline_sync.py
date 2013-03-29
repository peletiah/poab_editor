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
    log = request.json_body['log']
    print log
    url = 'http://poab.org:6543/sync?type=log'
    payload = {'log':json.dumps(log)}
    headers = {'content-type':'application/json'}
    r = requests.post(url, files=payload)
    sync_status=json.loads(r.text)['sync_status'] #if sync_status is True, we already have this image on the server
    print '\n>>>>>>> LOG SYNC STATUS: '+sync_status+str(log['id'])+'\n'
    return Response(r.text)




@view_config(route_name='sync', request_param='type=image')
def imagesync(request):
    image = Image.get_image_by_id(request.json_body['image']['id'])
    log = request.json_body['log']

    headers = {'content-type':'application/json'}
    url = 'http://poab.org:6543/sync?type=status'
    payload = {'type':'image', 'metadata':json.dumps(image.reprJSON())}
    r = requests.post(url, data=payload)

    sync_status=json.loads(r.text)['sync_status'] #if sync_status is True, we already have this image on the server
    print '\n################ IMAGE SYNC STATUS: '+sync_status+str(log['id']) + '\n'

    if sync_status == 'not_synced':
        image_bin = open(image.location+image.name, 'rb')
        url = 'http://poab.org:6543/sync?type=image'
        payload = {'metadata':json.dumps(image.reprJSON()), 'image_bin':image_bin, 'log':json.dumps(log)}
        headers = {'content-type':'application/json'}
        r = requests.post(url, files=payload)
        return Response(r.text)

    elif sync_status == 'was_synced':
        return Response(json.dumps({'item_uuid':image.uuid, 'log_id':log['id'], 'sync_status':sync_status}))

    return Response(json.dumps({'item_uuid':None, 'log_id':log['id'], 'sync_status':sync_status}))

@view_config(route_name='sync', request_param='type=track')
def tracksync(request):
    track = Track.get_track_by_id(request.json_body['track']['id'])
    log = request.json_body['log']


    headers = {'content-type':'application/json'}
    url = 'http://poab.org:6543/sync?type=status'
    payload = {'type':'track', 'metadata':json.dumps(track.reprJSON())}
    r = requests.post(url, data=payload)

    sync_status=json.loads(r.text)['sync_status'] #if sync_status is True, we already have this track on the server

    if not sync_status:
        track_bin = open(track.location+track.name, 'rb')
        url = 'http://poab.org:6543/sync?type=track'
        payload = {'metadata':json.dumps(track.reprJSON()), 'track_bin':track_bin, 'log':json.dumps(log)}
        headers = {'content-type':'application/json'}
        r = requests.post(url, files=payload)
        return Response(r.text)
 
    elif sync_status:
        return Response(json.dumps({'item_uuid':track.uuid, 'log_id':log['id'], 'sync_status':sync_status}))

    return Response(json.dumps({'item_uuid':None, 'log_id':log['id'], 'sync_status':sync_status}))

