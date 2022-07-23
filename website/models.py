
from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin



class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(150))
    email = db.Column(db.String(150), unique = True)
    study_name = db.Column(db.String(150))
    study_start_date = db.Column(db.String(150))
    study_end_date = db.Column(db.String(150))
    auth_token = db.Column(db.String(700))
    refresh_token = db.Column(db.String(500))
    scopes = db.Column(db.String(500))
    date = db.Column(db.DateTime(timezone = True), default = func.now())
    




