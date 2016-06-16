from flask import jsonify,request,g
from models import *
from app import app,db,auth
import helper_for_views
import fields
from datetime import datetime
import json

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"err":"404 error page not found"}),404

@app.errorhandler(403)
def not_authorized(e):
    return jsonify({"err":"You are not authorized to view this page"}),403

@app.errorhandler(400)
def something_missing(e):
    return jsonify({"err":"Arguments provided were not enough to carry out this request"})


def internal_error(s=""):
    return after_request({"err":"internal server error.","description":s})

def as_msg(s,errors=[]):
    return after_request({"err":"There seems to be some error","description":s,"errors":errors})

def as_success(s,warnings=[],errors=[]):
    d={}
    if not len(errors)==0:
        d["errors"]=errors
        d["partial_success"]=s
    if not len(warnings)==0:
        d["warnings"]=warnings
    if not d.has_key("partial_success"):
        d["success"]=s
    return after_request(d)

@auth.verify_password
def verify_password(username_or_token,password=None):
    admin=None
    company=None
    if request.json.has_key("company_token") and request.json.has_key("admin_token"):
        return False
    if request.json.has_key("company_token"):
        company=Company.verify_auth_token(request.json["company_token"])
        g.company=company
        return True
    elif request.json.has_key("admin_token"):
        admin=Admin.verify_auth_token(request.json["admin_token"])
        g.admin=admin
        return True
    else:
        return False

@app.route("/",methods=["GET","POST"])
@app.route("/index",methods=["GET","POST"])
def index():
    return as_success("application is working fine")


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
        main_fields=fields.company["primary"]
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


@app.route("/login",methods=["GET","POST"])
def login():
    try:
        data=request.json
    except:
        return as_msg("no json data could be extracted")
    if data.has_key("company_token"):
        return as_msg("company token already present")
    if data.has_key("admin_token"):
        return as_msg("admin token already present")
    data=helper_for_views.parse_to_proper(data)
    if not data.has_key("emailid"):
        return as_msg("no emailid provided")
    elif not data.has_key("password"):
        return as_msg("no password provided")
    emailid=data["emailid"]
    password=data["password"]
    company=Company.query.filter(Company.emailid==emailid)
    if company.count()==0:
        return as_msg("email/password not correct")
    else:
        company=company[0]
    if not company.check_password(password):
        return as_msg("email/password not correct")
    token=company.generate_auth_token()
    request.json["company_token"]=token
    return as_success("successfully logged in")

@app.route("/admin_login",methods=["GET","POST"])
def admin_login():
    try:
        data=request.json
    except:
        return as_msg("no json data could be extracted")
    if data.has_key("company_token"):
        return as_msg("company token already present")
    if data.has_key("admin_token"):
        return as_msg("admin token already present")
    data=helper_for_views.parse_to_proper(data)
    if not data.has_key("username"):
        return as_msg("no username provided")
    elif not data.has_key("password"):
        return as_msg("no password provided")
    username=data["username"]
    password=data["password"]
    admin=Admin.query.filter(Admin.username==username)
    if admin.count()==0:
        return as_msg("username/password not correct")
    else:
        admin=admin[0]
    if not admin.check_password(password):
        return as_msg("username/password not correct")
    token=admin.generate_auth_token()
    request.json["admin_token"]=token
    return as_success("successfully logged in")


@app.route("/get_modules",methods=["POST"])
@auth.login_required
def get_modules():
    try:
        all_modules=Module.query.all()
        modules=[]
        for module in all_modules:
            modules.append(module.serialize())
        return after_request({"modules":modules})
    except:
        return internal_error()

@app.route("/get_students",methods=["GET","POST"])
@auth.login_required
def get_students():
    try:
        id=int(request.json["module_id"].strip())
        module=Module.query.get(module_id)
        if not module:
            return as_msg("no such module found")
        students=[]
        for student in module.students:
            students.append(student.half_serialize())
        return after_request({"students":students})
    except:
        return internal_error()

@app.route("/get_student_details",methods=["GET","POST"])
@auth.login_required
def get_student_details():
    try:
        id=int(request.json["student_id"].strip())
        student=Student.query.get(student_id)
        if not student:
            return as_msg("no such student found")
        return after_request({"student_details":student})
    except:
        return internal_error()

@app.route("/create_schedule",methods=["GET","POST"])
def create_schedule():
    try:
        data=request.json
    except:
        return as_msg("could not extract json data")
    try:
        data=helper_for_views.parse_to_proper(data)
        main_fields=fields.schedule["mandatory"]
        errors=[]
        msg_errors=[]
        warnings=[]
        if not data.has_key("company_id"):
            errors.append("company_id is an essential field")
        if not data.has_key("students"):
            errors.append("students is an essential field though they it can be an empty list")
        for field in main_fields:
            if not field in data.keys():
                errors.append(field+" is an essential field")
        if not len(errors)==0:
            return as_msg("essential fields missing",errors)
        schedule=Schedule(name=data["name"])
        for field in data.keys():
            if not field in main_fields:
                warnings.append("schedule has no attribute "+field)
                continue
            if field=="name":
                continue
            setattr(schedule,field,data[field])
        db.session.add(schedule)
        db.session.flush()
        company=Company.query.get(data["company_id"].strip())
        if not company:
            return as_msg("no such company present")
        company.schedules.append(schedule)
        student_ids=data["students"]
        for student_id in student_ids:
            try:
                student=Student.query.get(int(student_id).strip())
                schedule.students.append(student)
            except:
                pass
        db.session.add(schedule)
        db.session.commit()
        return as_success("schedule added successfully")
    except:
        return internal_error()

@app.route("/get_schedule_details",methods=["GET","POST"])
def get_schedule_details():
    try:
        schedule_id=int(request.json["schedule_id"].strip())
    except:
        return as_msg("could not extract schedule_id")
    try:
        schedule=Schedule.query.get(schedule_id)
        if not schedule:
            return as_msg("no such schedule found")
        return after_request({"schedule_details":schedule.full_serialize()})
    except:
        return internal_error()



@app.route("/add_student",methods=["GET","POST"])
def add_student():
    try:
        data=request.json
    except:
        return as_msg("no json could be received")
    if not check_admin():
        return not_authorized("")
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
        student=Student(name=data["name"])
        for field in data.keys():
            if not field in main_fields:
                warnings.append("company has no attribute "+field)
                continue
            if field=="name" or field=="module_id":
                continue
            setattr(company,field,data[field])
        db.session.add(company)
        db.session.flush()
        try:
            module=Module.query.get(int(data["module_id"].strip()))
            if not module:
                return as_msg("no such module present")
        except:
            pass
        module.students.append(student)
        db.session.add(module)
        db.session.commit()
        return as_success("student added successfully")
    except:
        return internal_error()


@app.route("/delete_student",methods=["GET","POST"])
def delete_student():
    try:
        student_id=int(request.json["student_id"])
    except:
        return as_msg("no student id could be extracted")
    try:
        if not check_admin():
            return not_authorized("")
        student=Student.query.get(student_id)
        if student:
            db.session.delete(student)
            db.session.commit()
            return as_success("student has been deleted successfully")
        else:
            return as_msg("no such student exists")
    except:
        return internal_error()


@app.route("/delete_module",methods=["GET","POST"])
def delete_module():
    try:
        module_id=int(request.json["module_id"].strip())
    except:
        return as_msg("no module id could be extracted")
    try:
        if not check_admin():
            return not_authorized("")
        module=Module.query.get(module_id)
        if not module:
            return as_msg("no such module found")
        db.session.delete(module)
        db.session.commit()
        return as_success("module successfully deleted")
    except:
        return internal_error()

@app.route("/add_module",methods=["GET","POST"])
def add_module():
    try:
        data=request.json
    except:
        return as_msg("no json data could be extracted")
    try:
        if not check_admin():
            return not_authorized("")
        if not data.has_key("name"):
            return as_msg("name is an essential field")
        module=Module(data["name"].strip())
        if data.has_key("description"):
            module.description=data["description"].strip()
        db.session.add(module)
        db.session.commit()
        return as_success("module successfully added")
    except:
        return internal_error()



def check_admin():
    if request.json.has_key("admin_token"):
        admin=Admin.verify_auth_token(request.json["admin_token"])
        if admin:
            return True
    return False

def after_request(d):
    try:
        data=request.json
        if data.has_key("company_token"):
            d["company_token"]=data["company_token"]
        if data.has_key("admin_token"):
            d["admin_token"]=data["admin_token"]
        return jsonify(d)
    except:
        return jsonify(d)
