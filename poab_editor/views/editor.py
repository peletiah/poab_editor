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
    Etappe,
    Log,
    Image,
    Track,
    Trackpoint,
    Author,
    ComplexEncoder
    )

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden
    )

import hashlib, json
from poab_editor.helpers import (
    timetools,
    imagetools,
    filetools,
    gpxtools
    )

from time import strftime
import datetime
from datetime import timedelta
import json,uuid


@view_config(route_name='overview', renderer='overview.mako')
def overview(request):
    owner = authenticated_userid(request)
    author = Author.get_author(owner)
    if not author:
        loc = request.route_url('login')
        return HTTPFound(location=loc)
    if author.name == 'admin': #TODO
        logs = Log.get_logs()
    else:
        logs = Log.get_logs_by_author(author.id)
    if not logs:
        url = request.route_url('editor')
        return HTTPFound(location=url)
    logs_json = json.dumps([i.reprJSON() for i in logs],cls=ComplexEncoder)
    return {'logs': logs_json, 'author': author}
    
        
@view_config(
        route_name='editor',
        permission='create', 
        renderer='editor.mako'
)
@view_config(
        route_name='editor:logid',
        permission='edit', 
        renderer='editor.mako'
)
def editor(request):
    owner = authenticated_userid(request)
    author = Author.get_author(owner)
    if request.matchdict:
        log_id = request.matchdict['logid']
        log = Log.get_log_by_id(log_id)
        images_json = json.dumps([i.reprJSON() for i in log.image],cls=ComplexEncoder) #TODO: Order by timestamp_original
        tracks_json = json.dumps([i.reprJSON() for i in log.track],cls=ComplexEncoder)
        log_json = json.dumps(log.reprJSON(),cls=ComplexEncoder)
        if not log.etappe: #log.etappe might still be empty, so we create an empty array for AngularJS
            etappe_json = json.dumps(dict(id=None, start_date = None, end_date = None, name = None))
        else:
            etappe_json = json.dumps(log.etappe_ref.reprJSON(),cls=ComplexEncoder)
    else:
        #no existing record, so we send empty objects to the template
        images_json = json.dumps([dict(id=None, name=None, location=None, title=None, \
                        alt=None, comment=None, hash=None, author=None, \
                        last_change=None, published=None)])
        etappe_json = json.dumps(dict(id=None, start_date = None, end_date = None, name = None))
        tracks_json = json.dumps([dict(id=None, reduced_trackpoints = list(), distance=None, \
                        timespan=None, trackpoint_count=None, start_time = None, end_time = None, \
                        color=None, author=None, uuid=None, published=None)])
        log_json = json.dumps(dict(id=None,topic=None, content=None, author=None, created=None, \
                        last_change=None, published=None))
    etappe_datestr = Etappe.get_etappe_dropdown_list(5)
    etappe_datestr_json = json.dumps([i.reprJSON() for i in etappe_datestr])
    return {'images': images_json, 'etappe_datestr_json': etappe_datestr_json, 'etappe' : etappe_json, 'tracks' : tracks_json, 'log': log_json, 'author': author}


@view_config(route_name='delete_log')
def delete_log(request):
    log_json = request.json_body
    log_id = log_json['id']
    log = Log.get_log_by_id(log_id)
    print(log.id)
    DBSession.delete(log)
    DBSession.flush()
    return Response(log.topic)



@view_config(route_name='save_log')
def save_log(request):
    owner = authenticated_userid(request)
    author = Author.get_author(owner)
    log_json = request.json_body
    log_id = log_json['id']
    topic=log_json['topic']
    content=log_json['content']
    images = log_json['images']
    tracks = log_json['tracks']
    etappe = log_json['etappe']

    today=strftime("%Y-%m-%d")
    
    basedir = '/srv/trackdata/bydate'
    filedir = filetools.createdir(basedir, author.name, today) #TODO: 990-dir is created, img_large_w is ignored
    
    start_date = etappe['start_date']
    end_date = datetime.datetime.strptime(etappe['end_date'],'%Y-%m-%d') #unicode to datetime
    end_date = end_date+datetime.timedelta(days=1)-datetime.timedelta(seconds=1) #we need 23:59:59 this day, not 00:00:00
    name=etappe['name']

    if etappe['id']:
        print('etappe-id:'+ str(etappe['id']))
        etappe = Etappe.get_etappe_by_id(etappe['id'])
        etappe.start_date = start_date
        etappe.end_date = end_date
        etappe.name = name
    else:
        etappe = Etappe(start_date=start_date, end_date=end_date, name=name)
    DBSession.add(etappe)
    DBSession.flush()
 
    if log_id:
        log = Log.get_log_by_id(log_id)
        log.topic = topic
        log.content = content
        log.last_change = timetools.now()
        log.etappe = etappe.id
    else:
        #log_id is None, so this is a new post
        log = Log(topic=topic, content=content, author=author.id, etappe=etappe.id, created=timetools.now(), uuid=str(uuid.uuid4()))
    DBSession.add(log)
    DBSession.flush()
    print('logid='+str(log.id))
    for image in images:
        try:
            if image['id']:
                print('imageid:'+ str(image['id']))
                image = Image.get_image_by_id(image['id'])
                log.image.append(image)
        except Exception as e:
            print(e)
            print('ERROR while saving log')
    for track in tracks:
        if track['id']:
            print('trackid:'+ str(track['id']))
            track = Track.get_track_by_id(track['id'])
            log.track.append(track)
    return Response(json.dumps(dict(log_id=log.id, etappe_id=etappe.id),cls=ComplexEncoder))


 
@view_config(route_name='update_image_metadata')
def update_image_metadata(request):
    print(request.json_body)
    for image_dict in request.json_body:
        try:
            if image_dict['id']:
                image=Image.get_image_by_id(image_dict['id'])
                if image.title != image_dict['title'] or \
                image.alt != image_dict['alt'] or \
                image.comment != image_dict['comment']: #only update if there were changes            
                    image.title = image_dict['title']
                    image.alt = image_dict['alt']
                    image.comment = image_dict['comment']
                    image.last_change = timetools.now()
                    DBSession.add(image)
        except Exception as e:
            print(e)
            print('ERROR on updating metadata')
            
    return Response('ok')
 


@view_config(route_name='fileupload', request_param='type=image')
def imageupload(request):
    filelist = request.POST.getall('uploadedFile')
    upload = request.POST.get('upload')
    print(request.POST.get('upload'))
    print(request.POST.keys())
    print(filelist)
    
    owner = authenticated_userid(request)
    author = Author.get_author(owner)
    images_in_db = Image.get_images()
    today=strftime("%Y-%m-%d")
    
    basedir = '/srv/trackdata/bydate'
    img_large_w='990' #width of images in editor-preview
    img_medium_w='500' #width of images in editor-preview
    img_thumb_w='150' #width of images in editor-preview
    filedir = filetools.createdir(basedir, author.name, today) #TODO: 990-dir is created, img_large_w is ignored
    imgdir = filedir+'images/sorted/'
    images=list()

    for file in filelist:
        print('\n')
        print(file.filename)
        print('\n')
        filehash = hashlib.sha256(file.value).hexdigest()

        if not filetools.file_exists(images_in_db, filehash): #TODO: Uhm, wouldn't a simple db-query for the hash work too???
            if upload: #only save files when upload-checkbox has been ticked
                filehash = filetools.safe_file_local(imgdir, file)
                imagetools.resize(imgdir, imgdir+img_large_w+'/', file.filename, img_large_w)
                imagetools.resize(imgdir, imgdir+img_medium_w+'/', file.filename, img_medium_w)
                imagetools.resize(imgdir, imgdir+img_thumb_w+'/', file.filename, img_thumb_w)
            image = Image(name=file.filename, location=imgdir, title=None, comment=None, alt=None, \
                        aperture=None, shutter=None, focal_length=None, iso=None, timestamp_original=None, \
                        hash=filehash, hash_large=None, author=author.id, trackpoint=None, last_change=timetools.now(), \
                        published=None, uuid=str(uuid.uuid4()))
            image.aperture, image.shutter, image.focal_length, image.iso, image.timestamp_original = imagetools.get_exif(image)
            image.timestamp_original = image.timestamp_original#-timedelta(seconds=7200) #TODO
            trackpoint=gpxtools.sync_image_trackpoint(image)
            if trackpoint:
                image.trackpoint = trackpoint.id
            DBSession.add(image)
            DBSession.flush()
            image_json = image.reprJSON()
            images.append(image_json)
            print(images)
        else:
            image = Image.get_image_by_hash(filehash)
            image_json = image.reprJSON()
            images.append(image_json)
    #url = request.route_url('editor')
    #return HTTPFound(location=url)
    return Response(json.dumps({'images':images},cls=ComplexEncoder))


@view_config(route_name='delete_image')
def delete_image(request):
    image_json = request.json_body
    image_id = image_json['id']
    image = Image.get_image_by_id(image_id)
    print(image.id)
    DBSession.delete(image)
    DBSession.flush()
    return Response(image.name)




def add_trackpoints_to_db(trackpoints, track): 
    for trackpoint in trackpoints:
        trackpoint_in_db = Trackpoint.get_trackpoint_by_lat_lon_time(trackpoint.latitude, \
                                        trackpoint.longitude, trackpoint.timestamp)
        if not trackpoint_in_db:
            trackpoint.track_id = track.id

            try:
                DBSession.add(trackpoint)
                DBSession.flush()
                print(trackpoint.timestamp)
            except Exception as e:
                print("\n\nTrackpoint could not be added!\n\n")
                print(e)
                DBSession.rollback()


def add_track_to_db(track_details, author):
    track = track_details['track']
    trackpoints = track_details['trackpoints']
    track_in_db = Track.get_track_by_reduced_trackpoints(track.reduced_trackpoints)
    
    if not track_in_db:
        track.author = author.id
        track.uuid = str(uuid.uuid4())
        track.start_time = trackpoints[0].timestamp
        track.end_time = trackpoints[-1].timestamp
        try:
            DBSession.add(track)
            DBSession.flush()
        except Exception as e:
            DBSession.rollback()
            print("\n\nTrack could not be added!\n\n")
            print(e)
            return None
    else:
        track=track_in_db # We've found this track in the DB
    return track




@view_config(route_name='fileupload', request_param='type=track')
def trackupload(request):
    filelist = request.POST.getall('uploadedFile')
    upload = request.POST.get('upload')
    print(request.POST.get('upload'))
    print(request.POST.keys())
    print(filelist)
 
    owner = authenticated_userid(request)
    author = Author.get_author(owner)

    today=strftime("%Y-%m-%d")
    
    basedir = '/srv/trackdata/bydate'
    filedir = filetools.createdir(basedir, author.name, today)
    trackdir = filedir+'trackfile/'
    tracks_in_db = list()

    for file in filelist:
        if upload: #only save files when upload-checkbox has been ticked
            filehash = filetools.safe_file_local(trackdir, file)
            print('\n')
            print(file.filename)
            print('\n')

        parsed_tracks = gpxtools.parse_gpx(trackdir+file.filename)

        for track_details in parsed_tracks:
            track = add_track_to_db( track_details, author )
            if track:
                add_trackpoints_to_db( track_details['trackpoints'], track )
                tracks_in_db.append(track)

    return Response(json.dumps({'tracks':tracks_in_db},cls=ComplexEncoder))


















