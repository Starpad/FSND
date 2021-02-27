from sqlalchemy import Column, String, create_engine, Integer
from flask_sqlalchemy import SQLAlchemy
import json
import os

database_path = os.environ['postgres://qxhsqjslsrwmsi:985405ea19c92b7c58d6373d587169a140a2261441bb13e7cfafefec0235d532@ec2-54-87-34-201.compute-1.amazonaws.com:5432/d93ji6ce9det35']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Person
Have title and release year
'''
class Person(db.Model):  
  __tablename__ = 'People'

  id = Column(Integer, primary_key=True)
  name = Column(String)
  catchphrase = Column(String)

  def __init__(self, name, catchphrase=""):
    self.name = name
    self.catchphrase = catchphrase

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'catchphrase': self.catchphrase}