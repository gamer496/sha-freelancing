import os
from information import *

#main config
SQLALCHEMY_DATABASE_URI="mysql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_HOST+"/"+DB_NAME
SQLALCHEMY_TRACK_MODIFICATIONS=True
SECRET_KEY="reality is broken"
SECURITY_PASSWORD_SALT="email salt"
DEBUG=True
