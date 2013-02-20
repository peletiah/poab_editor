from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from poab_editor.models import (
    DBSession,
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
 


@view_config(route_name='new_entry', renderer='index.mako')
def new_entry(request):
    images = Image.get_images()
    images_json = json.dumps([i.reprJSON() for i in images],cls=ComplexEncoder)
    
    print images
    print 'bla'
    return {'images' : images_json, 'logtext': json.dumps('bla')}

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

            image = Image(name=file.filename, location=imgdir, title=None, comment=None, alt=None, hash=filehash, author=author.id, last_change=timetools.now())
            DBSession.add(image)

    url = request.route_url('new_entry')
    return HTTPFound(location=url)
