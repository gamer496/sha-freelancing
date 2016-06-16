from app import app,db
from app.models import Admin

username=raw_input("Enter the name of the new admin:\n").strip()
admins=Admin.query.filter(Admin.username==username)
if not admins.count()==0:
    print "admin with that name already exists.Cannot add that."
password=raw_input("Enter the password:\n")
admin=Admin(username=username,password=password)
try:
    db.session.add(admin)
    db.session.commit()
    print "admin added successfully."
except:
    print "problem occurred exiting now."
