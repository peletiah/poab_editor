from .models import (
    DBSession,
    Author,
    )


def groupfinder(name, request):
    author = Author.get_author(name)
    if author and author.group:
        return ['g:%s' % g.name for g in author.group]
    else:
        return [author.id]
