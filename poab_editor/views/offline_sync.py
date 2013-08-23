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
    log = Log.get_log_by_id(request.json_body['log']['id'])
    print log.id
    print log.reprJSON_extended()
    url = 'http://poab.org:6544/sync?type=log'
    payload = {'log_json':json.dumps(log.reprJSON_extended())}
    headers = {'content-type':'application/json'}
    remote_sync_info = requests.post(url, files=payload)
    sync_status=json.loads(remote_sync_info.text)['sync_status'] #if sync_status is True, we already have this image on the server
    if sync_status == 'is_synced':
        log.published = timetools.now()
        DBSession.add(log)
    return Response(remote_sync_info.text)
    #return Response(json.dumps({'log_id':log.id, 'type':'log', 'item_uuid':log.uuid, 'sync_status':'was_synced'}))



@view_config(route_name='sync', request_param='type=image')
def imagesync(request):
    image = Image.get_image_by_id(request.json_body['image']['id'])

    if not image.trackpoint: #find trackpoint for image if there was none yet
        trackpoint=gpxtools.sync_image_trackpoint(image)
        if trackpoint:
            image.trackpoint = trackpoint.id
            DBSession.add(image)
            DBSession.flush()
    log_json = request.json_body['log']
    log = Log.get_log_by_id(log_json['id'])

    headers = {'content-type':'application/json'}
    url = 'http://poab.org:6544/sync?type=status'
    payload = {'payloadtype':'image', 'image_json':json.dumps(image.reprJSON()), 'log_json':json.dumps(log.reprJSON())}
    remote_sync_info = requests.post(url, data=payload)
    print remote_sync_info.text
    sync_status=json.loads(remote_sync_info.text)['sync_status'] #if sync_status is 'was_synced', we already have this image on the server
    print '\n################ IMAGE SYNC STATUS: '+sync_status+str(log.id) + '\n'

    if sync_status == 'not_synced':
        #image_bin = open(image.location+image.name, 'rb')
        image_bin = ''
        url = 'http://poab.org:6544/sync?type=image'
        payload = {'image_json':json.dumps(image.reprJSON_extended()), 'image_bin':image_bin, 'log':json.dumps(log.reprJSON())}
        headers = {'content-type':'application/json'}
        remote_sync_info = requests.post(url, files=payload)

    return Response(remote_sync_info.text)
    #return Response(json.dumps({'log_id':log.id,'type':'image',  'item_uuid':image.uuid, 'sync_status':'was_synced'}))


@view_config(route_name='sync', request_param='type=track')
def tracksync(request):
    #print request.json_body
    track = Track.get_track_by_id(request.json_body['track']['id'])
    log_json = request.json_body['log']
    log = Log.get_log_by_id(log_json['id'])

    print track.reprJSON_extended()['author']


    headers = {'content-type':'application/json'}
    url = 'http://poab.org:6544/sync?type=status'
    payload = {'payloadtype':'track', 'track_json':json.dumps(track.reprJSON()), 'log_json':json.dumps(log.reprJSON())}
    remote_sync_info = requests.post(url, data=payload)
    print remote_sync_info.text
    sync_status=json.loads(remote_sync_info.text)['sync_status'] #if sync_status is 'was_synced', we already have this track on the server
    print '\n################ TRACK SYNC STATUS: '+sync_status+str(log.id) + '\n'
    #TODO: this prevents half uploaded trackpoints from beeing finished!!!!

    if sync_status == 'not_synced':
        headers = {'content-type':'application/json'}
        url = 'http://poab.org:6544/sync?type=track'
        payload = {'track':json.dumps(track.reprJSON_extended()), 'log_json':json.dumps(log.reprJSON())}
    
        remote_sync_info = requests.post(url, data=payload)
    
    return Response(remote_sync_info.text)
    #return Response(json.dumps({'log_id':log.id, 'type':'track', 'item_uuid':track.uuid, 'sync_status':'was_synced'}))

@view_config(route_name='sync', request_param='interlink')
def interlink(request):
    item_info_json = request.json_body
    sync_status = item_info_json['sync_status']
    type = item_info_json['type']
    uuid =  item_info_json['item_uuid']
    log_id = item_info_json['log_id']
    remote_sync_info = None

    if sync_status == 'is_synced' or sync_status == 'was_synced':
        if type == 'log':
            log = Log.get_log_by_uuid(uuid)
            headers = {'content-type':'application/json'}
            url = 'http://poab.org:6544/sync?interlink=log'
            payload = {'log_json':json.dumps(log.reprJSON_extended())}
            remote_sync_info = requests.post(url, data=payload)
        if type == 'image':
            image = Image.get_image_by_uuid(uuid)
            print image
            headers = {'content-type':'application/json'}
            url = 'http://poab.org:6544/sync?interlink=image'
            payload = {'image_json':json.dumps(image.reprJSON_extended())}
            remote_sync_info = requests.post(url, data=payload)
        if type == 'track':
            track = Track.get_track_by_uuid(uuid)
            print track
            headers = {'content-type':'application/json'}
            url = 'http://poab.org:6544/sync?interlink=track'
            payload = {'track_json':json.dumps(track.reprJSON_extended())}
            remote_sync_info = requests.post(url, data=payload)
    print remote_sync_info
    return Response(remote_sync_info.text)
    

#Directly sync all images to trackpoints
@view_config(route_name='sync', request_param='image_location')
def image_location(request):
    updated_images=list()
    images = Image.get_images()
    for image in images:
        if not image.trackpoint:
            print image.id
            trackpoint=gpxtools.sync_image_trackpoint(image)
            print trackpoint
            if trackpoint:
                image.trackpoint = trackpoint.id
                DBSession.add(image)
                DBSession.flush()
                updated_images.append(image.id)
    print updated_images
    return Response(str(updated_images))

