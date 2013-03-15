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


@view_config(
    route_name='authors',
    permission='admin',
    renderer='authors.mako',
)
def authors_view(request):
    owner = authenticated_userid(request)
    author = Author.get_author(owner)

    authors = DBSession.query(Author).all()
    return {
        'authors': sorted([a.name for a in authors]), 
        'author': author
    }

@view_config(
    route_name='author',
    permission='edit',
    renderer='author.mako',
)
def author_view(request):
    author = request.context
    print author
    logs = Log.get_logs_by_author(author.id)

    return {
        'author': author,
        'logs': logs,
    }


def validate_author(name, password):
    errors = []

    name = name.strip()
    if not name:
        errors.append('Name may not be empty')
    elif len(name) > 32:
        errors.append('Name may not be longer than 32 characters')

    password = password.strip()
    if not password:
        errors.append('Password may not be empty')

    return {
        'name': name,
        'password': password,
        'errors': errors,
    }


@view_config(
    route_name='create_author',
    renderer='edit_author.mako',
)
def create_author_view(request):
    errors = []
    name = password = ''
    if request.method == 'POST':
        name = request.POST.get('name', '')
        password = request.POST.get('password', '')

        v = validate_author(name, password)
        name = v['name']
        password = v['password']
        errors += v['errors']

        if not errors:
            author = Author(name=name, password=password)
            DBSession.add(author)
            url = request.route_url('login')
            return HTTPFound(location=url)

    return {
        'name': name,
        'password': password,
        'errors': errors,
    }
