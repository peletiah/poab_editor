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

    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/images/jpg',os.F_OK):
        pass
    else:
        os.mkdir(abspath+'/'+relpath1+'/'+relpath2+'/images/jpg')


    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted',os.F_OK):
        pass
    else:
        os.mkdir(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted')

    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted/990',os.F_OK):
        pass
    else:
        os.mkdir(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted/990')

    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted/500',os.F_OK):
        pass
    else:
        os.mkdir(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted/500')

    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted/thumb',os.F_OK):
        pass
    else:
        os.mkdir(abspath+'/'+relpath1+'/'+relpath2+'/images/sorted/thumb')

    if os.access(abspath+'/'+relpath1+'/'+relpath2+'/videos',os.F_OK):
        pass
    else:
        os.mkdir(abspath+'/'+relpath1+'/'+relpath2+'/videos')


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


def file_exists(files_in_db, filehash):
    for file in files_in_db:
        if file.hash == filehash:
            print("File %s already in DB" % file.location)
            return True
    return False
