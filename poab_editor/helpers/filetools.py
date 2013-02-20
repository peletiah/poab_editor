import os, hashlib


def createdir(abspath, relpath1, relpath2):
    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/images',os.F_OK):
        pass
    else:
        os.makedirs(abspath+'/'+relpath1+'/'+relpath2+'/images')

    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/images/raw',os.F_OK):
        pass
    else:
        os.mkdir(abspath+'/'+relpath1+'/'+relpath2+'/images/raw')

    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted',os.F_OK):
        pass
    else:
        os.mkdir(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted')

    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted/990',os.F_OK):
        pass
    else:
        os.mkdir(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted/990')

    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted/preview',os.F_OK):
        pass
    else:
        os.mkdir(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted/preview')

    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted/thumbs',os.F_OK):
        pass
    else:
        os.mkdir(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted/thumbs')


    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/trackfile',os.F_OK):
        pass
    else:
        os.mkdir(abspath+'/'+relpath1+'/'+relpath2+'/trackfile')
    return abspath+'/'+relpath1+'/'+relpath2+'/'


def safe_file_local(filelocation, file):
    f = open(filelocation+file.filename, 'w')
    f.write(file.value)
    f.close()
    return hashlib.sha256(open(filelocation+file.filename).read()).hexdigest()


def file_exists(images_in_db, filehash):
    for image in images_in_db:
        if image.hash == filehash:
            print "File %s already in DB" % image.location
            return True
    return False
