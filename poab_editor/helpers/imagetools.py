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
    print exif
    aperture = exif[0]['Aperture']
    shutter = exif[0]['ShutterSpeed']
    focal_length = exif[0]['FocalLength']
    iso = exif[0]['ISO']
    timestamp_original = datetime.datetime.strptime(exif[0]['DateTimeOriginal'], "%Y:%m:%d %H:%M:%S")
    print aperture, shutter, focal_length, iso, timestamp_original
    return aperture, shutter, focal_length, iso, timestamp_original
    
