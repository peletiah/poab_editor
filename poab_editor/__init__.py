from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from poab_editor.security import groupfinder

from poab_editor.models import (
    RootFactory as RootFactory,
    LogFactory as LogFactory,
    AuthorFactory as AuthorFactory
)

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    authn_policy = AuthTktAuthenticationPolicy(
        secret=settings['auth_tut.secret'],
        callback=role_filter,
        hashalg='sha512'
    )
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(
            settings=settings,
            authentication_policy=authn_policy,
            authorization_policy=authz_policy,
            root_factory=RootFactory,
    )
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('overview', '/')
    config.add_route('home', '/')



    config.add_route('editor:logid', '/editor/{logid}', factory=LogFactory,
                    traverse='{logid}')
    config.add_route('editor', '/editor', factory=LogFactory)

    config.add_route('fileupload', '/fileupload', factory=LogFactory)
    config.add_route('update_image_metadata', '/update_image_metadata', factory=LogFactory)

    config.add_route('save_log', '/save_log', factory=LogFactory)
    config.add_route('delete_log', '/delete', factory=LogFactory)
    config.add_route('preview', '/preview', factory=LogFactory)

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('authors', '/authors')
    config.add_route('author', '/author/{login}', factory=AuthorFactory,
                     traverse='/{login}')
    config.add_route('create_author', '/create_author', factory=AuthorFactory)

    config.add_route('groups', '/groups', factory=LogFactory)
    config.add_route('create_group', '/create_group', factory=LogFactory)
    config.add_route('edit_group', '/group/{name}/{action}', factory=LogFactory)

    config.scan()
    return config.make_wsgi_app()

