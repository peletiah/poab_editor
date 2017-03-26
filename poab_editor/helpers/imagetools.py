import os
import datetime
import json

def resize(fullsizepath,resizepath,imagename,width):
    if os.path.isdir(resizepath):
        pass
    else:
        os.mkdir(resizepath)
    os.system("/usr/bin/convert "+fullsizepath+"/"+imagename+" -resize "+width+" "+resizepath+"/"+imagename)
    #os.system("/usr/bin/convert "+fullsizepath+"/"+imagename.split(".")[0]+".jpg -resize "+width+" "+resizepath+"/"+imagename.split(".")[0]+".jpg")


def get_exif(image):
    exiftool = '/usr/bin/exiftool'
    exif = json.loads(
        os.popen(('%s -j -ShutterSpeed -Aperture -ISO -FocalLength -DateTimeOriginal %s%s') % (exiftool, image.location, image.name)).read()
    )
    print(exif)
    try:
        aperture = exif[0]['Aperture']
    except:
        aperture = None
    try:
        shutter = exif[0]['ShutterSpeed']
    except:
        shutter = None
    try:
        focal_length = exif[0]['FocalLength']
    except:
        focal_length = None
    try:
        iso = exif[0]['ISO']
    except:
        iso = None
    timestamp_original = datetime.datetime.strptime(exif[0]['DateTimeOriginal'], "%Y:%m:%d %H:%M:%S")
    print(aperture, shutter, focal_length, iso, timestamp_original)
    return aperture, shutter, focal_length, iso, timestamp_original
    
