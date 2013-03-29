Offline Editor for poab.org

Built with AngularJS and pyramids

    sudo apt-get install python2.7-dev libxslt1-dev libxml2-dev libpq-dev 
    #libpg-dev is optional, edit setup.py and remove psycopg2 if you use sqlite
    virtualenv env
    cd env
    git clone git@github.com:peletiah/poab_editor.git
    cd poab_editor
    ../bin/python setup.py develop
