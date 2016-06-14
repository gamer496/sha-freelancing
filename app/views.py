from flask import jsonify,request,g
from models import *
from app import app,db,auth
import helper_for_views
import fields
from datetime import datetime
import json


def internal_error(s=""):
    return jsonify({"err":"internal server error.","description":s})

def as_msg(s,errors=[]):
    return jsonify({"err":"There seems to be some error","description":s,"errors":errors})

def as_success(s,warnings=[],errors=[]):
    d={}
    if not len(errors)==0:
        d["errors"]=errors
        d["partial_success"]=s
    if not len(warnings)==0:
        d["warnings"]=warnings
    if not d.has_key("partial_success"):
        d["success"]=s
    return jsonify(d)

@auth.verify_password
def verify_password(token):
    admin=None
    company=None
    if request.json.has_key("company_token") and request.json.has_key("admin_token"):
        return False
    if request.json.has_key("company_token"):
        company=Company.verify_auth_token(request.json["company_token"])
    elif request.json.has_key("admin_token"):
        admin=Admin.verify_auth_token(request.json["admin_token"])
    if not admin and not company:
        return False
    else:
        if admin:
            g.admin=admin
            return True
        else:
            g.company=company
            return True

@app.route("/",methods=["GET","POST"])
@app.route("/index",methods=["GET","POST"])
def index():
    return as_msg("application is working fine")


@app.route("/registration",methods=["GET","POST"])
def registration():
    try:
        data=request.json
    except:
        return as_msg("no json could be received")
    if data.has_key("company_token"):
        return as_msg("already logged in")
    elif data.has_key("admin_token"):
        return as_msg("admin logged in")
    try:
        data=helper_for_views.parse_to_proper(data)
        main_fields=fields.company["mandatory"]
        errors=[]
        msg_errors=[]
        warnings=[]
        for field in main_fields:
            if not field in data.keys():
                errors.append(field+" is an essential field")
        if not len(errors)==0:
            return as_msg("essential fields missing",errors)
        for field in fields.company["unique"]:
            if getattr(Company,"check_"+field)(data[field])!=0:
                errors.append("object with "+field+" already exists")
        if not len(errors)==0:
            return as_msg("duplicate entries",errors)
        company=Company(name=data["name"],password=data["password"])
        for field in data.keys():
            if not field in main_fields:
                warnings.append("company has no attribute "+field)
                continue
            if field=="name" or field=="password":
                continue
            setattr(company,field,data[field])
        db.session.add(company)
        db.session.commit()
        token=company.generate_auth_token()
        request.json["company_token"]=token
        return as_success("company added successfully")
    except:
        return internal_error()

@app.after_request
def after(response):
    d=json.loads(response.get_data())
    data=request.json
    if data.has_key("company_token"):
        d["company_token"]=data["company_token"]
    if data.has_key("admin_token"):
        d["admin_token"]=data["admin_token"]
    response.set_data(json.dumps(d))
    return response
