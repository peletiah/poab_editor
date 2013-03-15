from pyramid.response import Response

from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    HTTPForbidden
    )

from pyramid.view import view_config
from pyramid.view import forbidden_view_config

from sqlalchemy.exc import DBAPIError

from pyramid.security import (
    authenticated_userid,
    forget,
    remember
)

from poab_editor.models import (
    DBSession,
    Author,
    Log,
    )

@forbidden_view_config()
def forbidden_view(request):
    if authenticated_userid(request):
        return HTTPForbidden()

    loc = request.route_url('login', _query=(('next', request.path),))
    return HTTPFound(location=loc)

@view_config(
    route_name='login',
    renderer='login.mako',
)
def login_view(request):
    next = request.params.get('next') or request.route_url('overview')
    name = ''
    did_fail = False
    authors = DBSession.query(Author).all()
    if 'submit' in request.POST:
        name = request.POST.get('name', '')
        password = request.POST.get('password', '')
        author = Author.get_author(name)
        if author and author.validate_password(password):
            headers = remember(request, name)
            return HTTPFound(location=next, headers=headers)
        did_fail = True

    return {
        'name': name,
        'next': next,
        'failed_attempt': did_fail,
        'authors': authors,
        'request': request
    }

@view_config(
    route_name='logout',
)
def logout_view(request):
    headers = forget(request)
    loc = request.route_url('home')
    return HTTPFound(location=loc, headers=headers)


