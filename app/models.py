from app import app,db
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,BadSignature,SignatureExpired)
from datetime import datetime


studentschedules=db.Table("studentschedules",
        db.Column("student_id",db.Integer,db.ForeignKey("student.id")),
        db.Column("schedule_id",db.Integer,db.ForeignKey("schedule.id"))
        )

class Admin(db.Model):
    __tablename__="admin"
    id          =db.Column      (db.Integer,primary_key=True)
    username    =db.Column      (db.String(200),unique=True)
    password    =db.Column      (db.String(200))

    def __init__(self,username,password):
        self.username=username
        self.set_password(password)

    def set_password(self,password):
        self.password=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)

    def generate_auth_token(self):
        s=Serializer(app.config["SECRET_KEY"])
        return s.dumps({"id":self.id})

    @staticmethod
    def verify_auth_token(token):
        s=Serializer(app.config["SECRET_KEY"])
        try:
            data=s.loads(token)
        except BadSignature:
            return None
        user=Admin.query.get(data["id"])
        return user

    def __repr__(self):
        return "Admin : %s"%(self.name)


class Company(db.Model):
    __tablename__="company"
    id              =db.Column      (db.Integer,primary_key=True)
    name            =db.Column      (db.String(200))
    password        =db.Column      (db.String(200))
    pan_no          =db.Column      (db.String(50),unique=True)
    tin_no          =db.Column      (db.String(50),unique=True)
    phone_no        =db.Column      (db.String(50),unique=True)
    landline_no     =db.Column      (db.String(50),unique=True)
    contact_person  =db.Column  (db.String(200))
    emailid         =db.Column      (db.String(50),unique=True,index=True)
    member_since    =db.Column      (db.DateTime)
    schedules       =db.relationship("Schedule",backref="company",lazy="dynamic")

    def __init__(self,name,password):
        self.name=name
        self.set_password(password)
        self.member_since=datetime.utcnow()

    def set_password(self,password):
        self.password=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)

    def generate_auth_token(self):
        s=Serializer(app.config["SECRET_KEY"])
        return s.dumps({"id":self.id})

    @staticmethod
    def verify_auth_token(token):
        s=Serializer(app.config["SECRET_KEY"])
        try:
            data=s.loads(token)
        except BadSignature:
            return None
        user=Company.query.get(data["id"])
        return user

    @staticmethod
    def check_phone_no(phone_no):
        return Company.query.filter(Company.phone_no==phone_no).count()

    @staticmethod
    def check_landline_no(landline_no):
        return Company.query.filter(Company.landline_no==landline_no).count()

    @staticmethod
    def check_emailid(emailid):
        return Company.query.filter(Company.emailid==emailid).count()

    @staticmethod
    def check_pan_no(pan_no):
        return Company.query.filter(Company.pan_no==pan_no).count()

    @staticmethod
    def check_tin_no(tin_no):
        return Company.query.filter(Company.tin_no==tin_no).count()

    def half_serialize(self):
        d={}
        d["id"]=self.id
        d["name"]=self.name
        d["emailid"]=self.emailid
        return d

    def full_serialize(self):
        d={}
        d=self.half_serialize()
        d["phone_no"]=self.phone_no
        d["landline_no"]=self.landline_no
        d["pan_no"]=self.pan_no
        d["tin_no"]=self.tin_no
        d["contact_person"]=self.contact_person
        return d

    def __repr__(self):
        return "<Company : %s"%(self.name)


class Module(db.Model):
    __tablename__="module"
    id          =db.Column      (db.Integer,primary_key=True)
    name        =db.Column      (db.String(200),unique=True)
    description =db.Column      (db.TEXT)
    students    =db.relationship("Student",backref="module",lazy="dynamic")

    def __init__(self,name):
        self.name=name

    def serialize(self):
        d={}
        d["id"]=self.id
        d["name"]=self.name
        if self.description:
            d["description"]=self.description
        else:
            d["description"]=""
        return d

    def __repr__(self):
        return "Module : %s"%(self.name)

class Student(db.Model):
    __tablename__="student"
    id          =db.Column      (db.Integer,primary_key=True)
    name        =db.Column      (db.String(200))
    degree      =db.Column      (db.String(200))
    city        =db.Column      (db.String(200))
    phone_no    =db.Column      (db.String(20))
    emailid     =db.Column      (db.String(200))
    college     =db.Column      (db.TEXT)
    description =db.Column      (db.TEXT)
    module_id   =db.Column      (db.Integer,db.ForeignKey("module.id"))
    schedules   =db.relationship("Schedule",secondary="studentschedules",backref=db.backref("students",lazy="dynamic"))

    def __init__(self,name):
        self.name=name

    def half_serialize(self):
        d={}
        d["id"]=self.id
        d["name"]=self.name
        d["description"]=self.description
        return d

    def full_serialize(self):
        d=self.half_serialize()
        d["degree"]=self.degree
        d["college"]=self.college
        d["module_id"]=self.module_id
        d["city"]=self.city
        d["emailid"]=self.emailid
        d["phone_no"]=self.phone_no
        return d

    def __repr__(self):
        return "Student : %s"%(self.student)


class Schedule(db.Model):
    __tablename__="schedule"
    id          =db.Column      (db.Integer,primary_key=True)
    address     =db.Column      (db.TEXT)
    date        =db.Column      (db.String(50))
    time        =db.Column      (db.String(50))
    company_id  =db.Column      (db.Integer,db.ForeignKey("company.id"))

    def __init__(self,company_id):
        self.company_id=company_id

    def half_serialize(self):
        d={}
        d["id"]=self.id
        d["address"]=self.address

    def full_serialize(self):
        d=self.half_serialize()
        d["date"]=self.date
        d["time"]=self.time
        d["company_id"]=self.company_id
        return d

    def __repr__(self):
        return "Schedule at: %s"%(self.address)
