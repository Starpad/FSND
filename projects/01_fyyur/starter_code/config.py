import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
# Enable debug mode.
DEBUG = True
# Connect to the database

# TODO IMPLEMENT DATABASE URL
# I chose to have a passwort for my db, as you can see in the string below
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:padpw@localhost:5432/fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False
