from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    VOTER = 'voter'
    CANDIDATE = 'candidate'

class User(db.Model):
    __tablename__ = 'users'  # Explicitly naming the table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), default=UserRole.VOTER, nullable=False)

class Vote(db.Model):
    __tablename__ = 'votes'  # Explicitly naming the table if not done so by convention
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)  # Referencing 'users.id'
    candidate_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships (optional, for easier reverse access in queries)
    voter = db.relationship('User', foreign_keys=[user_id], backref=db.backref('votes_cast', lazy='dynamic'))
    candidate = db.relationship('User', foreign_keys=[candidate_id], backref=db.backref('votes_received', lazy='dynamic'))
