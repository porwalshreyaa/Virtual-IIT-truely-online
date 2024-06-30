from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

user_meeting = db.Table('user_meeting',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('meeting_id', db.Integer, db.ForeignKey('meeting.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    homies = db.relationship(
        'User', 
        secondary='homie_association', 
        primaryjoin='User.id==HomieAssociation.user_id', 
        secondaryjoin='User.id==HomieAssociation.homie_id', 
        backref='friends'
    )
    created_events = db.relationship('Event', backref='creator', lazy=True)
    created_meetings = db.relationship('Meeting', backref='creator', lazy=True)
    meetings = db.relationship('Meeting', secondary=user_meeting, back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class HomieAssociation(db.Model):
    __tablename__ = 'homie_association'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    homie_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Event {self.name}>'

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    google_meet_link = db.Column(db.String(200), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    users = db.relationship('User', secondary=user_meeting, back_populates='meetings')

    def __repr__(self):
        return f'<Meeting {self.location}>'
