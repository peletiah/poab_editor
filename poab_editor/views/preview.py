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

import hashlib, json,re
from poab_editor.helpers import (
    timetools,
    imagetools,
    filetools
    )

from time import strftime


@view_config(route_name='preview', renderer='preview.mako')
def preview(request):
    if request.query_string:
        log_id = request.GET.get('logid')
        log = Log.get_log_by_id(log_id)
        imgid_list = re.findall("(\[imgid\d{1,}\])", log.content)
        preview = log.content
        for imgid in imgid_list:
            print imgid
            id = re.search("^\[imgid(\d{1,})\]$",imgid).group(1) #gets the id in [imgid123]
            image = Image.get_image_by_id(id)
            if image:
                if image.comment:
                    preview=preview.replace(imgid,'''<div class="log_inlineimage"><div class="imagecontainer"><img class="inlineimage" src="/static%spreview/%s" alt="%s"></div>
                                                     <span class="imagedescription">%s</span></div>''' % (image.location, image.name, image.alt, image.comment))
                else:
                   preview = preview.replace(imgid,'''<div class="log_inlineimage"> <div class="imagecontainer"><img class="inlineimage" src="/static%spreview/%s" alt="%s">
                                                      </div></div>''' % (image.location, image.name, image.alt))
                    #preview = preview.replace(imgid,'<img src="static'+image.location+'preview/'+image.name+'">')
    return {'log': log, 'preview': preview}
    

