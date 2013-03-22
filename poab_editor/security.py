from .models import (
    DBSession,
    Author,
    )


def role_filter(name, request):
    author = Author.get_author(name)
    if author and author.group:
        return ['g:%s' % g.name for g in author.group]
    else:
        try:
            return [author.id]
        except AttributeError:
            print 'No author defined yet'
            return None
