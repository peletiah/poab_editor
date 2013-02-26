from sqlalchemy import (
    Table,
    ForeignKey,
    Column,
    Integer,
    Text,
    types,
    UniqueConstraint
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

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


### Class and Table Definitions

log_image_table = Table('log_image', Base.metadata,
    Column('log_id', Integer, ForeignKey('log.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('image_id', Integer, ForeignKey('image.id',onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint('log_id', 'image_id', name='log_id_image_id'))


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
        return dict(id=self.id, topic=self.topic, content=self.content, author=self.author, \
                    created = self.created.strftime("%Y-%m-%d %H:%M:%S"), \
                    last_change=self.last_change.strftime("%Y-%m-%d %H:%M:%S"), published=self.published)

    @classmethod
    def get_logs(self):
        logs = DBSession.query(Log).all()
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
    log = relation('Log', secondary=log_image_table, backref='logref')
    __table_args__ = (
        UniqueConstraint('location', 'name', name='location_name'),
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
            published = self.published.strftime("%Y-%m-%d %H:%M:%S")
        else:
            published = self.published
        return dict(id=self.id, name=self.name, location=self.location, title=self.title, 
                    alt=self.alt, comment=self.comment, hash=self.hash, author=self.author,
                    last_change=self.last_change.strftime("%Y-%m-%d %H:%M:%S"), published=published)

    @classmethod
    def get_images(self):
        images = DBSession.query(Image).all()
        return images

    @classmethod
    def get_image_by_id(self, id):
        image = DBSession.query(Image).filter(Image.id == id).one()
        return image


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_author(self, name):
        author = DBSession.query(Author).filter(Author.name == name).one()
        return author


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)

