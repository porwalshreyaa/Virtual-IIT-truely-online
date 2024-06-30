from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

homies = db.Table(
    'homies',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('homie_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    meetings = db.relationship('Meeting', lazy=True)
    user_homies = db.relationship('User', secondary=homies, primaryjoin=(homies.c.user_id == id), 
                             secondaryjoin=(homies.c.homie_id == id), 
                             backref=db.backref('homies', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Event {self.name}>'

user_meeting = db.Table('user_meeting',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('meeting_id', db.Integer, db.ForeignKey('meetings.id'), primary_key=True)
)

class Meeting(db.Model):
    __tablename__ = 'meetings'

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    google_meet_link = db.Column(db.String(200), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    users = db.relationship('User', secondary=user_meeting, back_populates='meetings')

    def __repr__(self):
        return f'<Meeting {self.location}>'
