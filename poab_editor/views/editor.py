from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from poab_editor.models import (
    DBSession,
    Log,
    Image,
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
    filetools
    )

from time import strftime
import json


@view_config(route_name='overview', renderer='overview.mako')
def overview(request):
    logs = Log.get_logs()
    if not logs:
        url = request.route_url('editor')
        return HTTPFound(location=url)
    logs_json = json.dumps([i.reprJSON() for i in logs],cls=ComplexEncoder)
    return {'logs': logs_json}
    
        


@view_config(route_name='update_log')
def update_log(request):
    print request.json_body
    log_json = request.json_body
    id = log_json['id']
    topic=log_json['topic']
    content=log_json['content']
    print 'id: '+str(id)
    print 'topic: '+str(topic)
    print 'content: '+str(content)
    author = 1 #TODO: Replace with proper credentials from request
    if id:
        log = Log.get_log_by_id(id)
        log.topic = topic
        log.content = content
        log.last_change = timetools.now()
    else:
        #log_id is None, so this is a new post
        log = Log(topic=topic, content=content, author=author)
        print log.id
    DBSession.add(log)
        
    
        
    return Response('ok')
 
@view_config(route_name='update_image_metadata')
def update_image_metadata(request):
    print request.json_body
    for image_dict in request.json_body:
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
 


@view_config(route_name='editor', renderer='editor.mako')
def editor(request):
    if request.query_string:
        print 'Query string is '+str(request.GET.get('logid'))
        log_id = request.GET.get('logid')
        log = Log.get_log_by_id(log_id)
        print log.id
        images = Image.get_images()
        images_json = json.dumps([i.reprJSON() for i in images],cls=ComplexEncoder)
        log_json = json.dumps(log.reprJSON(),cls=ComplexEncoder)
        print log_json
        return {'images' : images_json, 'log': log_json}
    else:
        #no existing record, so we send empty objects to the template
        images_json = json.dumps([dict(id=None, name=None, location=None, title=None, \
                        alt=None, comment=None, hash=None, author=None, \
                        last_change=None, published=None)])
        print images_json
        log_json = json.dumps(dict(id=None,topic=None, content=None, author=None, created=None, \
                        last_change=None, published=None))
        #images_json = [json.dumps(dict())]
        return {'images': images_json, 'log': log_json}

@view_config(route_name='fileupload')
def fileupload(request):
    filelist = request.POST.getall('files')
    upload = request.POST.get('upload')
    print request.POST.get('upload')
    print request.POST.keys()

    author = Author.get_author('Christian')
    images_in_db = Image.get_images()
    
    today=strftime("%Y-%m-%d")
    
    basedir = '/srv/trackdata/bydate'
    img_prvw_w='500' #width of images in editor-preview
    img_thumb_w='150' #width of images in editor-preview
    filedir = filetools.createdir(basedir, author.name, today)
    imgdir = filedir+'images/sorted/'

    for file in filelist:
        filehash = hashlib.sha256(file.value).hexdigest()

        if not filetools.file_exists(images_in_db, filehash):
            if upload: #only save files when upload-checkbox has been ticked
                filehash = filetools.safe_file_local(imgdir, file)
                imagetools.resize(imgdir, imgdir+'preview/', file.filename, img_prvw_w)
                imagetools.resize(imgdir, imgdir+'thumbs/', file.filename, img_thumb_w)

            image = Image(name=file.filename, location=imgdir, title=None, comment=None, alt=None, hash=filehash, author=author.id, last_change=timetools.now(), published=None)
            DBSession.add(image)

    url = request.route_url('editor')
    return HTTPFound(location=url)
