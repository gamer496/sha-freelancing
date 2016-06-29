from app import app,db
from app.models import Student

while True:
    try:
        n=int(raw_input("Enter the number of students to enter.\n")).strip()
        break
    except:
        print "not a valid integer"

for i in range(0,n):
    name=raw_input("Enter name.\n").strip()
    description=raw_input("Enter description.\n").strip()
    degree=raw_input("Enter degree.\n").strip()
    college=raw_input("Enter college.\n").strip()
    try:
        student=Student(name)
        student.description=description
        student.degree=degree
        student.college=college
        while True:
            while True:
                try:
                    n=int(raw_input("Enter the module_id.\n").strip())
                    break
                except:
                    print "not a valid integer"
            module=Module.query.get(n)
            if not module:
                print "not a valid module.\n"
            else:
                break
        module.students.append(student)
        db.session.add(student)
        db.session.commit()
    except:
        print "err could not add to database"
