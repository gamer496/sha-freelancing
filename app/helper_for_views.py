import json
from datetime import datetime
from models import *


def parse_to_proper(data):
    data1={}
    for key in data.keys():
        if key.strip()=="password":
            data1["password"]=data[key]
            continue
        if isinstance(data[key],type("")):
            data1[key.strip()]=data[key].strip()
        else:
            data1[key.strip()]=data[key]
    return data1
