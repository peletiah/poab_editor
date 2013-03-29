Offline Editor for poab.org

Built with AngularJS and pyramids

    sudo apt-get install python2.7-dev libxslt1-dev libxml2-dev libpq-dev 
    #libpg-dev is optional, edit setup.py and uncomment psycopg2 if you use postgresql
    virtualenv env
    cd env
    git clone git@github.com:peletiah/poab_editor.git
    cd poab_editor
    ../bin/initialize_poab_editor_db development.ini
    ../bin/python setup.py develop
    
