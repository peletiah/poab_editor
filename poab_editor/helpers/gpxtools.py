from lxml import etree
from xml.etree import ElementTree

from datetime import timedelta
import time,datetime

import json

from decimal import Decimal, ROUND_HALF_UP

import poab_editor.helpers.douglaspeucker as dp



def reduce_trackpoints(trackpoints):
    points = []
    for pt in trackpoints:
        points.append(dp.Vec2D( float(pt.longitude) , float(pt.latitude) ))
    line = dp.Line(points)
    return line.simplify(0.0002)


def create_json_for_db(reduced_tkpts):
            trackpoint_list = list()
            for trackpoint in reduced_tkpts.points:
                trackpoint_list.append([trackpoint.coords[0],trackpoint.coords[1]])
            json_string=json.dumps(dict(type='Feature',geometry=dict(type='LineString',coordinates=trackpoint_list)))
            return json_string


def gpxprocess(gpxfile):
    file = open(gpxfile,'r')
    class trkpt:
        def __init__(self, latitude, longitude):
            self.latitude = latitude
            self.longitude = longitude

    trkptlist=list()

    gpx_ns = "http://www.topografix.com/GPX/1/1"

    root = etree.parse(gpxfile).getroot()
    trackSegments = root.getiterator("{%s}trkseg"%gpx_ns)
    for trackSegment in trackSegments:
        for trackPoint in trackSegment:
            lat=trackPoint.attrib['lat']
            lon=trackPoint.attrib['lon']
            new_trkpt=trkpt(lat,lon)
            trkptlist.append(new_trkpt)

    reduced_trkpts=reduce_trackpoints(trkptlist)
    json_string=create_json_for_db(reduced_trkpts)
    file.close()
    return json_string

