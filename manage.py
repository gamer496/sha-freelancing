from app import app,db,migrate,manager
from flask_migrate import MigrateCommand
from config import SQLALCHEMY_DATABASE_URI

@manager.command
def runserver():
    app.run()
manager.add_command('db',MigrateCommand)

if __name__=="__main__":
    manager.run()
