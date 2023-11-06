import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, ForeignKey 
from sqlalchemy import select


from sqlalchemy.orm import Session 
from sqlalchemy.orm import declarative_base 
from sqlalchemy.orm import relationship

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from applications.database import db

current_dir = os.path.abspath(os.path.dirname(__file__))

Base = declarative_base()

app = None

def create_app():
	app = Flask(__name__, template_folder="templates")
	app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+ os.path.join(current_dir, "musicDB.sqlite3")
	db.init_app(app)
	app.app_context().push ()
	return app

app = create_app()
from applications.controllers import *

if __name__ == '__main__':
	app.static_folder = 'static'
	app.run(debug=True)