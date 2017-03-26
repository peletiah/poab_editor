from sqlalchemy import (
    Table,
    ForeignKey,
    Column,
    Integer,
    Text,
    types,
    UniqueConstraint,
    Unicode,
    and_
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.dialects import postgresql


from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
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

#import hashlib
from passlib.hash import pbkdf2_sha256
#from poab_editor.helpers.pbkdf2.pbkdf2 import pbkdf2_bin
from os import urandom
from base64 import b64encode, b64decode
import uuid as uuidlib
import re

izip = zip

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
    Column('image_id', Integer, ForeignKey('image.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint('log_id', 'image_id', name='log_id_image_id'))

log_track_table = Table('log_track', Base.metadata,
    Column('log_id', Integer, ForeignKey('log.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('track_id', Integer, ForeignKey('track.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint('log_id', 'track_id', name='log_id_track_id'))


author_group_table = Table('author_group', Base.metadata,
    Column('author_id', Integer, ForeignKey('author.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('group.id', onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint('author_id', 'group_id', name='author_id_group_id'))



class Etappe(Base):
    __tablename__ = 'etappe'
    id = Column(Integer, primary_key=True)
    start_date = Column(types.TIMESTAMP(timezone=False),default=timetools.now())
    end_date = Column(types.TIMESTAMP(timezone=False),default=timetools.now())
    uuid = Column(Text, unique=True)
    name = Column(Text)
    log = relationship('Log', backref='etappe_ref')
    #track = relationship('Track', backref='etappe')
    __table_args__ = (
        UniqueConstraint('start_date', 'end_date', name='etappe_start_end'),
        {}
        )
    
    def __init__(self, start_date=timetools.now(), end_date=timetools.now(), name=None, uuid=str(uuidlib.uuid4())):
        self.start_date = start_date
        self.end_date = end_date
        self.name = name
        self.uuid = uuid


    def reprJSON(self):
        start_date = self.start_date.strftime("%Y-%m-%d")
        end_date = self.end_date.strftime("%Y-%m-%d")
        return dict(id=self.id, start_date=start_date, end_date=end_date, name=self.name, uuid=self.uuid)


    @classmethod
    def get_etappen(self):
        etappen = DBSession.query(etappe).order_by(start_date.desc()).all()
        return etappen

    @classmethod
    def get_etappe_dropdown_list(self, limit):
        #returns a Etappe-Object with additional attribute "date_str"
        #date_str is a prettified merge of "start_date" and "end_date"
        etappen = DBSession.query(Etappe).order_by(Etappe.start_date.desc()).limit(limit).all()
        etappe_dropdown_list=list()
        for etappe in etappen:
            day_str = month_str = year_str = date_str = None
            if etappe.start_date.year == etappe.end_date.year:
                year_str = etappe.start_date.year

            if etappe.start_date.month == etappe.end_date.month:
                month_str = etappe.start_date.strftime('%B')

            if etappe.start_date.day == etappe.end_date.day:
                day_str = etappe.start_date.day

            date_str = etappe.start_date.strftime('%d. %B %Y - ')+etappe.end_date.strftime('%d. %B %Y')

            if year_str: #only years are the same
                date_str = etappe.start_date.strftime('%d. %B - ')+etappe.end_date.strftime('%d. %B %Y')

            if month_str and year_str: #year and month are the same
                date_str = etappe.start_date.strftime('%d. - ')+etappe.end_date.strftime('%d. %B %Y')
            
            if day_str and month_str and year_str: #day, month and year are the same
                date_str = etappe.start_date.strftime('%d. %B %Y')

            class EtappeDropdown(object):
                def __init__(self, id, start_date, end_date, date_str, name, uuid):
                    self.id = id
                    self.start_date = start_date
                    self.end_date = end_date
                    self.date_str = date_str
                    self.name = name
                    self.uuid = uuid 
            
                def reprJSON(self):
                    start_date = self.start_date.strftime("%Y-%m-%d")
                    end_date = self.end_date.strftime("%Y-%m-%d")
                    return dict(id=self.id, start_date=start_date, end_date=end_date, date_str=self.date_str, name=self.name, uuid=self.uuid)
    
            etappe_dropdown = EtappeDropdown(etappe.id, etappe.start_date, etappe.end_date, date_str, etappe.name, etappe.uuid)

            etappe_dropdown_list.append(etappe_dropdown)
        return etappe_dropdown_list



    @classmethod
    def get_etappe_by_id(self, id):
        etappe = DBSession.query(Etappe).filter(Etappe.id == id).one()
        return etappe

    @classmethod
    def get_etappe_by_uuid(self, uuid):
        etappe = DBSession.query(Etappe).filter(Etappe.uuid == uuid).one()
        return etappe



class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    topic = Column(Text)
    content = Column(Text)
    author = Column(Integer, ForeignKey('author.id', onupdate="CASCADE", ondelete="CASCADE"))
    etappe = Column(Integer, ForeignKey('etappe.id', onupdate="CASCADE", ondelete="CASCADE"))
    created = Column(types.TIMESTAMP(timezone=False), default=timetools.now())
    last_change = Column(types.TIMESTAMP(timezone=False), default=timetools.now())
    published = Column(types.TIMESTAMP(timezone=False))
    uuid = Column(Text, unique=True)
    image = relationship('Image', secondary=log_image_table, backref='logs', passive_deletes=True, order_by="asc(Image.timestamp_original)")
    track = relationship('Track', secondary=log_track_table, backref='logs')
    #etappe = relationship("Etappe", backref="logs", order_by="desc(Etappe.start_date)")

    @property
    def __acl__(self):
        return [
            (Allow, self.author, 'edit'),
        ]

    
    def __init__(self, topic, content, author, etappe, uuid, created=timetools.now(), \
                last_change=timetools.now(), published=None):
        self.topic = topic
        self.content = content
        self.author = author
        self.etappe = etappe
        self.created = created
        self.last_change = last_change
        self.published = published
        self.uuid = uuid
    
    def reprJSON(self):
        if self.published:
            published = self.published.strftime("%Y-%m-%d %H:%M:%S")
        else:
            published = self.published
        author = Author.get_author_by_id(self.author)
        etappe = Etappe.get_etappe_by_id(self.etappe)
        images = [i.reprJSON() for i in self.image]
        tracks = [i.reprJSON() for i in self.track]
        return dict(id=self.id, topic=self.topic, content=self.content, author=author.name, \
                    etappe = etappe.reprJSON(), created = self.created.strftime("%Y-%m-%d %H:%M:%S"), \
                    last_change=self.last_change.strftime("%Y-%m-%d %H:%M:%S"), published=published, \
                    images=images, tracks=tracks, uuid=self.uuid)
    

    def reprJSON_extended(self):
        if self.published:
            published = self.published.strftime("%Y-%m-%d %H:%M:%S")
        else:
            published = self.published
        author = Author.get_author_by_id(self.author)
        etappe = Etappe.get_etappe_by_id(self.etappe)
        images = [i.reprJSON() for i in self.image]
        tracks = [i.reprJSON() for i in self.track]
        content_img_uuid_tags = self.imgid_tag_to_img_uuid_tag() #replace [imgid123]-tags with [img_uuid=123]-tags
        return dict(id=self.id, topic=self.topic, content=content_img_uuid_tags, author=author.name, \
                    etappe = etappe.reprJSON(), created = self.created.strftime("%Y-%m-%d %H:%M:%S"), \
                    last_change=self.last_change.strftime("%Y-%m-%d %H:%M:%S"), published=published, \
                    images=images, tracks=tracks, uuid=self.uuid)
 
    
    def imgid_tag_to_img_uuid_tag(self):
        imgid_list = re.findall("(\[imgid\d{1,}\])", self.content)
        content_with_uuid_tags = self.content
        for imgid in imgid_list:
            tag_id = re.search("^\[imgid(\d{1,})\]$",imgid).group(1) #gets the numeric id in [imgid123]
            image = Image.get_image_by_id(tag_id)
            if image:
                content_with_uuid_tags=content_with_uuid_tags.replace(imgid,('[img_uuid=%s]') % image.uuid)
        return content_with_uuid_tags



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

    @classmethod
    def get_log_by_uuid(self, uuid):
        log = DBSession.query(Log).filter(Log.uuid == uuid).one()
        return log



class Image(Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    location = Column(Text)
    title = Column(Text)
    comment = Column(Text)
    alt = Column(Text)
    aperture = Column(Text)
    shutter = Column(Text)
    focal_length = Column(Text)
    iso = Column(Text)
    timestamp_original = Column(types.TIMESTAMP(timezone=False))
    hash = Column(Text)
    hash_large = Column(Text) #hash of the image with 990px width
    author = Column(Integer, ForeignKey('author.id',onupdate="CASCADE", ondelete="CASCADE"))
    trackpoint = Column(Integer, ForeignKey('trackpoint.id',onupdate="CASCADE", ondelete="CASCADE"))
    last_change = Column(types.TIMESTAMP(timezone=False),default=timetools.now())
    published = Column(types.TIMESTAMP(timezone=False))
    uuid = Column(Text, unique=True)
    log = relationship('Log', secondary=log_image_table, passive_deletes=True,  backref='images')
    __table_args__ = (
        UniqueConstraint('location', 'name', name='image_location_name'),
        {}
        )
    


    def __init__(self, name, location, title, comment, alt, aperture, shutter, focal_length, iso, \
                timestamp_original, hash, hash_large, author, trackpoint, uuid, last_change=timetools.now(), \
                published=None):
        self.name = name
        self.location = location
        self.title = title
        self.comment = comment
        self.alt = alt
        self.aperture = aperture
        self.shutter = shutter
        self.focal_length = focal_length
        self.iso = iso
        self.timestamp_original = timestamp_original
        self.hash = hash
        self.hash_large = hash_large
        self.author = author
        self.trackpoint = trackpoint
        self.last_change = last_change
        self.published = published
        self.uuid = uuid

    def reprJSON(self):
        if self.published:
            published = self.published.strftime("%Y-%m-%d")
        else:
            published = self.published
        return dict(id=self.id, name=self.name, location=self.location, title=self.title, 
                    alt=self.alt, comment=self.comment, hash=self.hash, hash_large=self.hash_large,
                    last_change=self.last_change.strftime("%Y-%m-%d"), published=published, uuid=self.uuid)

    def reprJSON_extended(self):
        if self.published:
            published = self.published.strftime("%Y-%m-%d")
        else:
            published = self.published
        timestamp_original = self.timestamp_original.strftime("%Y-%m-%d %H:%M:%S") 
        author = Author.get_author_by_id(self.author)
        trackpoint = Trackpoint.get_trackpoint_by_id(self.trackpoint)
        if trackpoint:
            trackpoint = trackpoint.reprJSON()
        return dict(id=self.id, name=self.name, location=self.location, title=self.title, comment=self.comment, 
                    alt=self.alt, aperture=self.aperture, shutter=self.shutter, 
                    focal_length=self.focal_length, iso=self.iso, timestamp_original=timestamp_original, 
                    hash=self.hash, hash_large=self.hash_large,
                    author=author.reprJSON(), trackpoint=trackpoint, 
                    last_change=self.last_change.strftime("%Y-%m-%d"), published=published, uuid=self.uuid)




    @classmethod
    def get_images(self):
        images = DBSession.query(Image).order_by(Image.timestamp_original).all()
        return images

    @classmethod
    def get_image_by_id(self, id):
        try:
            image = DBSession.query(Image).filter(Image.id == id).one()
            return image
        except Exception as e:
            print("Error retrieving image {0}: ".format(e))
            return None

    @classmethod
    def get_image_by_uuid(self, uuid):
        try:
            image = DBSession.query(Image).filter(Image.uuid == uuid).one()
            return image
        except Exception as e:
            print("Error retrieving image %s: ",e)
            return None


    @classmethod
    def get_image_by_hash(self, hash):
        image = DBSession.query(Image).filter(Image.hash == hash).one()
        return image

class Track(Base):
    __tablename__ = 'track'
    id = Column(Integer, primary_key=True)
    reduced_trackpoints = Column("reduced_trackpoints", Text)
    distance = Column("distance", Text)
    timespan = Column("timespan", types.Interval)
    trackpoint_count = Column(Integer)
    start_time = Column("start_time", types.TIMESTAMP(timezone=False))
    end_time = Column("end_time", types.TIMESTAMP(timezone=False))
    color = Column("color", Text, default='FF0000')
    author = Column(Integer, ForeignKey('author.id',onupdate="CASCADE", ondelete="CASCADE"))
    uuid = Column(Text, unique=True)
    published = Column(types.TIMESTAMP(timezone=False))
    trackpoints = relationship("Trackpoint", backref="tracks", order_by="desc(Trackpoint.timestamp)")
    log = relationship('Log', secondary=log_track_table, backref='tracks')
 
    def __init__(self, reduced_trackpoints, distance, timespan, trackpoint_count, 
                start_time, end_time, color, author, uuid, published=None):
        self.reduced_trackpoints = reduced_trackpoints
        self.distance = distance
        self.timespan = timespan
        self.trackpoint_count = trackpoint_count
        self.start_time = start_time
        self.end_time = end_time
        self.color = color
        self.author = author
        self.uuid = uuid
        self.published = published

    def reprJSON(self): #returns own columns only
        if self.published:
            published = self.published.strftime("%Y-%m-%d")
        else:
            published = self.published
        start_time = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time = self.end_time.strftime("%Y-%m-%d %H:%M:%S")
        return dict(id=self.id, reduced_trackpoints=self.reduced_trackpoints, distance=str(self.distance), 
                    timespan=str(self.timespan), trackpoint_count=self.trackpoint_count, start_time=start_time,
                    end_time=end_time, color=self.color, uuid=self.uuid, published=published) 
                    #TODO:distance is a decimal, string is not a proper conversion


    def reprJSON_extended(self): #returns own and associated columns(deep query, takes longer)
        if self.published:
            published = self.published.strftime("%Y-%m-%d")
        else:
            published = self.published
        author = Author.get_author_by_id(self.author)
        trackpoints = [i.reprJSON() for i in self.trackpoints]
        log = [i.reprJSON() for i in self.log]
        start_time = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time = self.end_time.strftime("%Y-%m-%d %H:%M:%S")
        return dict(id=self.id, reduced_trackpoints=self.reduced_trackpoints, distance=str(self.distance), 
                    timespan=str(self.timespan), trackpoint_count=self.trackpoint_count, start_time=start_time,
                    end_time=end_time, color=self.color, author=author.name, uuid=self.uuid, published=published, 
                    trackpoints=trackpoints, log=log) #TODO:distance is a decimal, string is not a proper conversion



    @classmethod
    def get_tracks(self):
        tracks = DBSession.query(Track).all()
        return tracks

    @classmethod
    def get_track_by_id(self, id):
        track = DBSession.query(Track).filter(Track.id == id).one()
        return track

    @classmethod
    def get_track_by_uuid(self, uuid):
        track = DBSession.query(Track).filter(Track.uuid == uuid).one()
        return track

    @classmethod
    def get_track_by_reduced_trackpoints(self, reduced_trackpoints):
        try:
            track = DBSession.query(Track).filter(Track.reduced_trackpoints == reduced_trackpoints).one()
            return track
        except Exception as e:
            print("Error retrieving track %s: ",e)
            return None


class Trackpoint(Base):
    __tablename__ = 'trackpoint'
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    track_id = Column("track_id", types.Integer, ForeignKey('track.id'))
    latitude = Column("latitude", types.Numeric(9,7))
    longitude = Column("longitude", types.Numeric(10,7))
    altitude = Column("altitude", types.Integer)
    velocity = Column("velocity", types.Integer)
    temperature = Column("temperature", types.Integer)
    direction = Column("direction", types.Integer)
    pressure = Column("pressure", types.Integer)
    timestamp = Column("timestamp", types.TIMESTAMP(timezone=False))
    uuid = Column(Text, unique=True)
    images = relationship("Image", backref="trackpoints")
    tracks_ref = relationship("Track", backref="trackpoints_ref")
    __table_args__ = (
        UniqueConstraint('latitude', 'longitude', 'timestamp', name='lat_lon_timestamp'),
        {}
        )

    def __init__(self, track_id, latitude, longitude, altitude, velocity, temperature, direction, pressure, timestamp, uuid):
        self.track_id = track_id
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.velocity = velocity
        self.temperature = temperature
        self.direction = direction
        self.pressure = pressure
        self.timestamp = timestamp
        self.uuid = uuid


    def reprJSON(self):
        timestamp = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        latitude = str(self.latitude)
        longitude = str(self.longitude)
        return dict(id=self.id, latitude=latitude, longitude=longitude, 
                    altitude=self.altitude, velocity=self.velocity, temperature=self.temperature, 
                    direction=self.direction, pressure=self.pressure, timestamp=timestamp, uuid=self.uuid)  
    
    @classmethod
    def get_trackpoint_by_id(self, id):
        try:
            trackpoint = DBSession.query(Trackpoint).filter(Trackpoint.id == id ).one()
            return trackpoint
        except Exception as e:
            print ("Error retrieving trackpoint by id(%s):\n %s ") % (id, e)
            return None



    @classmethod
    def get_trackpoint_by_lat_lon_time(self, latitude, longitude, timestamp):
        try:
            trackpoint = DBSession.query(Trackpoint).filter(and_(Trackpoint.latitude == latitude, Trackpoint.longitude == longitude, Trackpoint.timestamp == timestamp)).one()
            return trackpoint
        except Exception as e:
            print ("Error retrieving trackpoint by lat(%s), lon(%s), time(%s) :\n %s ") % (latitude, longitude, timestamp, e)
            return None

    @classmethod
    def get_trackpoints_by_timerange(self, start_timestamp, end_timestamp):
        try:
            trackpoints = DBSession.query(Trackpoint).filter(and_(Trackpoint.timestamp >= start_timestamp, Trackpoint.timestamp <= end_timestamp)).all()
            return trackpoints
        except Exception as e:
            print ("Error retrieving trackpoints by timerange %s - %s %s: ") % (start_timestamp, end_timestamp, e)
            return []




class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    password = Column(Unicode(80), nullable=False)
    uuid = Column(Text, unique=True)
    logs = relationship("Log", backref="author_ref")
    tracks = relationship("Track", backref="author_ref")
    images = relationship("Image", backref="author_ref")
    group = relationship('Group', secondary=author_group_table, backref='memberships')

    @property
    def __acl__(self):
        return [
            (Allow, self.name, 'edit'),
        ]

    def __init__(self, name, password, uuid):
        self.name = name
        self._make_hash(password)
        self.uuid = uuid

    def reprJSON(self):
        return dict(id=self.id, name=self.name, uuid=self.uuid)

#    def _make_hash(self, password):
#        """Generate a random salt and return a new hash for the password."""
#        #if isinstance(password, unicode):
#        #    password = password.encode('utf-8')
#        salt = b64encode(urandom(SALT_LENGTH))
#        print('#############')
#        print(salt)
#        hashed_password =  'PBKDF2$%s$%i$%s$%s' % (
#            HASH_FUNCTION,
#            COST_FACTOR,
#            salt,
#            b64encode(pbkdf2_bin(password, salt, COST_FACTOR, KEY_LENGTH,
#                                 getattr(hashlib, HASH_FUNCTION))))
#        self.password = hashed_password

    def validate_password(cls, password):
        #cls is used instead of self, see PEP-8
        print('verify_password with {0}, {1}'.format(password,cls.password))
        print(pbkdf2_sha256.hash(password))
        try:
    	    if pbkdf2_sha256.verify(password,cls.password):
    	        return True
    	    else:
    	        return False
        except Exception as e:
            print('Error verifying password: {0}'.format(e))
            return False

#    def validate_password(self, password):
#        """Check a password against an existing hash."""
#        password = password.encode('utf-8')
#        print(password)
#        algorithm, hash_function, cost_factor, salt, hash_a = self.password.split('$')
#        assert algorithm == 'PBKDF2'
#        salt=bytes(salt,'utf-8')
#        hash_a = b64decode(hash_a)
#        print(self.password)
#        hash_b = pbkdf2_bin(password, salt, int(cost_factor), len(hash_a),
#                            getattr(hashlib, hash_function))
#        assert len(hash_a) == len(hash_b)  # we requested this from pbkdf2_bin()
#        # Same as "return hash_a == hash_b" but takes a constant time.
#        # See http://carlos.bueno.org/2011/10/timing.html
#        diff = 0
#        for char_a, char_b in izip(hash_a, hash_b.encode('utf-8')):
#            print(char_a, char_b)
#            diff |= ord(char_a) ^ ord(char_b)
#        return diff == 0

    def _set_password(self, password):
        hashed_password = password

        #if isinstance(password, unicode):
        #    password_8bit = password.encode('UTF-8')
        #else:
        #    password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()

        #if not isinstance(hashed_password, unicode):
        #    hashed_password = hashed_password.decode('UTF-8')

        self.password = hashed_password

    @classmethod
    def get_author(self, name):
        try:
            author = DBSession.query(Author).filter(Author.name == name).one()
            return author
        except Exception as e:
            print("Error retrieving author %s: ",e) 
            return None

    @classmethod
    def get_author_by_id(self, id):
        author = DBSession.query(Author).filter(Author.id == id).one()
        return author


class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    authors = relationship('Author', secondary=author_group_table, backref='members')

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

