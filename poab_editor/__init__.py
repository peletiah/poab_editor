from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import DBSession

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('overview', '/')
    config.add_route('editor', '/editor')
    config.add_route('edit_entry', '/{entry}/edit')
    config.add_route('fileupload', '/fileupload')
    config.add_route('update_image_metadata', '/update_image_metadata')
    config.add_route('update_log', '/update_log')
    config.scan()
    return config.make_wsgi_app()

