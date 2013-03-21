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

import hashlib, json
from poab_editor.helpers import (
    timetools,
    imagetools,
    filetools,
    gpxtools
    )

from time import strftime
import json


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
        images_json = json.dumps([i.reprJSON() for i in log.image],cls=ComplexEncoder)
        tracks_json = json.dumps([i.reprJSON() for i in log.track],cls=ComplexEncoder)
        log_json = json.dumps(log.reprJSON(),cls=ComplexEncoder)
    else:
        #no existing record, so we send empty objects to the template
        images_json = json.dumps([dict(id=None, name=None, location=None, title=None, \
                        alt=None, comment=None, hash=None, author=None, \
                        last_change=None, published=None)])
        tracks_json = json.dumps([dict(id=None, name=None, location=None, \
                        hash=None, author=None, published=None)])
        log_json = json.dumps(dict(id=None,topic=None, content=None, author=None, created=None, \
                        last_change=None, published=None))
    return {'images': images_json, 'tracks' : tracks_json, 'log': log_json, 'author': author}


@view_config(route_name='delete_log')
def delete_log(request):
    log_json = request.json_body
    id = log_json['id']
    log = Log.get_log_by_id(id)
    print log.id
    DBSession.delete(log)
    DBSession.flush()
    return Response(log.topic)



@view_config(route_name='save_log')
def save_log(request):
    owner = authenticated_userid(request)
    author = Author.get_author(owner)
    log_json = request.json_body
    id = log_json['id']
    topic=log_json['topic']
    content=log_json['content']
    images = log_json['images']
    tracks = log_json['tracks']
    if id:
        log = Log.get_log_by_id(id)
        log.topic = topic
        log.content = content
        log.last_change = timetools.now()
    else:
        #log_id is None, so this is a new post
        log = Log(topic=topic, content=content, author=author.id, created=timetools.now())
    DBSession.add(log)
    DBSession.flush()
    print 'logid='+str(log.id)
    for image in images:
        if image['id']:
            print 'imageid:'+ str(image['id'])
            image = Image.get_image_by_id(image['id'])
            log.image.append(image)
    for track in tracks:
        if track['id']:
            print 'trackid:'+ str(track['id'])
            track = Track.get_track_by_id(track['id'])
            log.track.append(track)
    return Response(str(log.id))


 
@view_config(route_name='update_image_metadata')
def update_image_metadata(request):
    print request.json_body
    for image_dict in request.json_body:
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
    return Response('ok')
 


@view_config(route_name='fileupload', request_param='type=image')
def imageupload(request):
    filelist = request.POST.getall('uploadedFile')
    upload = request.POST.get('upload')
    print request.POST.get('upload')
    print request.POST.keys()
    print filelist
    
    owner = authenticated_userid(request)
    author = Author.get_author(owner)
    images_in_db = Image.get_images()
    today=strftime("%Y-%m-%d")
    
    basedir = '/srv/trackdata/bydate'
    img_prvw_w='500' #width of images in editor-preview
    img_thumb_w='150' #width of images in editor-preview
    filedir = filetools.createdir(basedir, author.name, today)
    imgdir = filedir+'images/sorted/'
    images=list()

    for file in filelist:
        print '\n'
        print file.filename
        print '\n'
        filehash = hashlib.sha256(file.value).hexdigest()

        if not filetools.file_exists(images_in_db, filehash):
            if upload: #only save files when upload-checkbox has been ticked
                filehash = filetools.safe_file_local(imgdir, file)
                imagetools.resize(imgdir, imgdir+'preview/', file.filename, img_prvw_w)
                imagetools.resize(imgdir, imgdir+'thumbs/', file.filename, img_thumb_w)
            image = Image(name=file.filename, location=imgdir, title=None, comment=None, alt=None, hash=filehash, hash_990=None, author=author.id, last_change=timetools.now(), published=None)
            DBSession.add(image)
            DBSession.flush()
            image_json = image.reprJSON()
            images.append(image_json)
            print images
        else:
            image = Image.get_image_by_hash(filehash)
            image_json = image.reprJSON()
            images.append(image_json)
    #url = request.route_url('editor')
    #return HTTPFound(location=url)
    return Response(json.dumps({'images':images},cls=ComplexEncoder))

@view_config(route_name='fileupload', request_param='type=track')
def trackupload(request):
    filelist = request.POST.getall('uploadedFile')
    upload = request.POST.get('upload')
    print request.POST.get('upload')
    print request.POST.keys()
    print filelist
 
    owner = authenticated_userid(request)
    author = Author.get_author(owner)

    tracks_in_db = Track.get_tracks()
    today=strftime("%Y-%m-%d")
    
    basedir = '/srv/trackdata/bydate'
    filedir = filetools.createdir(basedir, author.name, today)
    trackdir = filedir+'trackfile/'
    tracks = list()

    for file in filelist:
        filehash = hashlib.sha256(file.value).hexdigest()

        if not filetools.file_exists(tracks_in_db, filehash):
            if upload: #only save files when upload-checkbox has been ticked
                filehash = filetools.safe_file_local(trackdir, file)
            trackdata_json = gpxtools.gpxprocess(trackdir+file.filename)
            print trackdata_json
            track = Track(name=file.filename, location=trackdir, geojson=trackdata_json, hash=filehash, author=author.id, published=None)
            DBSession.add(track)
            DBSession.flush()
            track_json = track.reprJSON()
            tracks.append(track_json)
        else:
            track = Track.get_track_by_hash(filehash)
            track_json = track.reprJSON()
            tracks.append(track_json)
        print track_json
        print tracks
    return Response(json.dumps({'tracks':tracks},cls=ComplexEncoder))
