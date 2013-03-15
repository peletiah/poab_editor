from sqlalchemy import (
    Table,
    ForeignKey,
    Column,
    Integer,
    Text,
    types,
    UniqueConstraint,
    Unicode
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relation
    )

from poab_editor.helpers import timetools
import json

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import (
    Allow,
    Everyone,
    Authenticated,
    authenticated_userid,
    forget,
    remember,
    ALL_PERMISSIONS
    )

import hashlib
from poab_editor.helpers.pbkdf2.pbkdf2 import pbkdf2_bin
from os import urandom
from base64 import b64encode, b64decode
from itertools import izip


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


SALT_LENGTH = 12
KEY_LENGTH = 24
HASH_FUNCTION = 'sha256'  # Must be in hashlib.
# Linear to the hashing time. Adjust to be high but take a reasonable
# amount of time on your server. Measure with:
# python -m timeit -s 'import passwords as p' 'p.make_hash("something")'
COST_FACTOR = 10000


### Class and Table Definitions

log_image_table = Table('log_image', Base.metadata,
    Column('log_id', Integer, ForeignKey('log.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('image_id', Integer, ForeignKey('image.id',onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint('log_id', 'image_id', name='log_id_image_id'))


log_track_table = Table('log_track', Base.metadata,
    Column('log_id', Integer, ForeignKey('log.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('track_id', Integer, ForeignKey('track.id',onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint('log_id', 'track_id', name='log_id_track_id'))


author_group_table = Table('author_group', Base.metadata,
    Column('author_id', Integer, ForeignKey('author.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('group.id',onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint('author_id', 'group_id', name='author_id_group_id'))

class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    topic = Column(Text)
    content = Column(Text)
    author = Column(Integer, ForeignKey('author.id',onupdate="CASCADE", ondelete="CASCADE"))
    created = Column(types.TIMESTAMP(timezone=False),default=timetools.now())
    last_change = Column(types.TIMESTAMP(timezone=False),default=timetools.now())
    published = Column(types.TIMESTAMP(timezone=False))
    image = relation('Image', secondary=log_image_table, backref='imageref')
    track = relation('Track', secondary=log_track_table, backref='trackref')

    @property
    def __acl__(self):
        return [
            (Allow, self.author, 'edit'),
        ]

    
    def __init__(self, topic, content, author, created=timetools.now(), \
                last_change=timetools.now(), published=None):
        self.topic = topic
        self.content = content
        self.author = author
        self.created = created
        self.last_change = last_change
        self.published = published
    
    def reprJSON(self):
        if self.published:
            published = self.published.strftime("%Y-%m-%d %H:%M:%S")
        else:
            published = self.published
        author = Author.get_author_by_id(self.author)
        return dict(id=self.id, topic=self.topic, content=self.content, author=author.name, \
                    created = self.created.strftime("%Y-%m-%d %H:%M:%S"), \
                    last_change=self.last_change.strftime("%Y-%m-%d %H:%M:%S"), published=published)

    @classmethod
    def get_logs(self):
        logs = DBSession.query(Log).order_by(Log.created.desc()).all()
        return logs

    @classmethod
    def get_logs_by_author(self, author_id):
        logs = DBSession.query(Log).filter(Log.author == author_id).order_by(Log.created.desc()).all()
        return logs



    @classmethod
    def get_log_by_id(self, id):
        log = DBSession.query(Log).filter(Log.id == id).one()
        return log



class Image(Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    location = Column(Text)
    title = Column(Text)
    comment = Column(Text)
    alt = Column(Text)
    hash = Column(Text)
    author = Column(Integer, ForeignKey('author.id',onupdate="CASCADE", ondelete="CASCADE"))
    last_change = Column(types.TIMESTAMP(timezone=False),default=timetools.now())
    published = Column(types.TIMESTAMP(timezone=False))
    log = relation('Log', secondary=log_image_table, backref='imagelogref')
    __table_args__ = (
        UniqueConstraint('location', 'name', name='image_location_name'),
        {}
        )
    


    def __init__(self, name, location, title, comment, alt, hash, author, last_change=timetools.now(), published=None):
        self.name = name
        self.location = location
        self.title = title
        self.alt = alt
        self.comment = comment
        self.hash = hash
        self.author = author
        self.last_change = last_change
        self.published = published

    def reprJSON(self):
        if self.published:
            published = self.published.strftime("%Y-%m-%d")
        else:
            published = self.published
        return dict(id=self.id, name=self.name, location=self.location, title=self.title, 
                    alt=self.alt, comment=self.comment, hash=self.hash, author=self.author,
                    last_change=self.last_change.strftime("%Y-%m-%d"), published=published)

    @classmethod
    def get_images(self):
        images = DBSession.query(Image).all()
        return images

    @classmethod
    def get_image_by_id(self, id):
        try:
            image = DBSession.query(Image).filter(Image.id == id).one()
            return image
        except Exception, e:
            print "Error retrieving extension %s: ",e
            return None

    @classmethod
    def get_image_by_hash(self, hash):
        image = DBSession.query(Image).filter(Image.hash == hash).one()
        return image


class Track(Base):
    __tablename__ = 'track'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    location = Column(Text)
    geojson = Column(Text)
    hash = Column(Text)
    author = Column(Integer, ForeignKey('author.id',onupdate="CASCADE", ondelete="CASCADE"))
    published = Column(types.TIMESTAMP(timezone=False))
    log = relation('Log', secondary=log_track_table, backref='tracklogref')
    __table_args__ = (
        UniqueConstraint('location', 'name', name='track_location_name'),
        {}
        )
    


    def __init__(self, name, location, geojson, hash, author, published=None):
        self.name = name
        self.location = location
        self.geojson = geojson
        self.hash = hash
        self.author = author
        self.published = published

    def reprJSON(self):
        if self.published:
            published = self.published.strftime("%Y-%m-%d")
        else:
            published = self.published
        return dict(id=self.id, name=self.name, location=self.location, geojson=self.geojson,
                    hash=self.hash, author=self.author, published=published)

    @classmethod
    def get_tracks(self):
        tracks = DBSession.query(Track).all()
        return tracks

    @classmethod
    def get_track_by_id(self, id):
        track = DBSession.query(Track).filter(Track.id == id).one()
        return track

    @classmethod
    def get_track_by_hash(self, hash):
        track = DBSession.query(Track).filter(Track.hash == hash).one()
        return track


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    password = Column(Unicode(80), nullable=False)
    group = relation('Group', secondary=author_group_table, backref='memberships')

    @property
    def __acl__(self):
        return [
            (Allow, self.name, 'edit'),
        ]

    def __init__(self, name, password):
        self.name = name
        self._make_hash(password)

    def _make_hash(self, password):
        """Generate a random salt and return a new hash for the password."""
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        salt = b64encode(urandom(SALT_LENGTH))
        hashed_password =  'PBKDF2$%s$%i$%s$%s' % (
            HASH_FUNCTION,
            COST_FACTOR,
            salt,
            b64encode(pbkdf2_bin(password, salt, COST_FACTOR, KEY_LENGTH,
                                 getattr(hashlib, HASH_FUNCTION))))
        self.password = hashed_password

    def validate_password(self, password):
        """Check a password against an existing hash."""
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        print password
        algorithm, hash_function, cost_factor, salt, hash_a = self.password.split('$')
        assert algorithm == 'PBKDF2'
        hash_a = b64decode(hash_a)
        hash_b = pbkdf2_bin(password, salt, int(cost_factor), len(hash_a),
                            getattr(hashlib, hash_function))
        assert len(hash_a) == len(hash_b)  # we requested this from pbkdf2_bin()
        # Same as "return hash_a == hash_b" but takes a constant time.
        # See http://carlos.bueno.org/2011/10/timing.html
        diff = 0
        for char_a, char_b in izip(hash_a, hash_b):
            diff |= ord(char_a) ^ ord(char_b)
        return diff == 0

    def _set_password(self, password):
        hashed_password = password

        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()

        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self.password = hashed_password

    @classmethod
    def get_author(self, name):
        try:
            author = DBSession.query(Author).filter(Author.name == name).one()
            return author
        except Exception, e:
            return None

    @classmethod
    def get_author_by_id(self, id):
        author = DBSession.query(Author).filter(Author.id == id).one()
        return author


class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    authors = relation('Author', secondary=author_group_table, backref='members')

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_group(self, name):
        group = DBSession.query(Group).filter(Group.name == name).one()
        return group




class RootFactory(object):
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request

class AuthorFactory(object):
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        author = Author.get_author(key)
        author.__parent__ = self
        author.__name__ = key
        return author

class LogFactory(object):
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'create'),
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request

    def __getitem__(self, key):
        log = Log.get_log_by_id(key)
        log.__parent__ = self
        log.__name__ = key
        return log





class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)

