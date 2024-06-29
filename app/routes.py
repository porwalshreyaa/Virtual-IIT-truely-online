from flask import Blueprint, render_template, redirect, url_for, session, current_app, request, flash
from app import app, db, socketio
from app.models import User, Meeting, Event
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import send
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
# from app.forms import RegistrationForm
from flask_oauthlib.client import OAuth
import requests
from app import db, login_manager



auth = Blueprint('auth', __name__)

oauth = OAuth()

google = oauth.remote_app(
    'google',
    consumer_key=current_app.config.get('GOOGLE_CLIENT_ID'),
    consumer_secret=current_app.config.get('GOOGLE_CLIENT_SECRET'),
    request_token_params={
        'scope': 'email',
    },
    base_url=current_app.config.get('GOOGLE_DISCOVERY_URL'),
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@auth.route('/google/login')
def google_login():
    return google.authorize(callback=url_for('auth.google_authorized', _external=True))

@auth.route('/google/callback')
def google_authorized():
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    
    session['google_token'] = (resp['access_token'], '')
    user_info = google.get('userinfo')
    email = user_info.data['email']
    # Handle user creation and login
    # Example:
    # user = User.query.filter_by(email=email).first()
    # if not user:
    #     user = User(email=email)
    #     db.session.add(user)
    #     db.session.commit()
    # login_user(user)
    return redirect(url_for('main.home'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')


@app.route('/')
@login_required
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/create_meeting', methods=['GET', 'POST'])
@login_required
def create_meeting():
    if request.method == 'POST':
        location = request.form.get('location')
        time = datetime.strptime(request.form.get('time'), '%Y-%m-%dT%H:%M')
        google_meet_link = request.form.get('google_meet_link')
        meeting = Meeting(location=location, time=time, google_meet_link=google_meet_link, creator_id=current_user.id)
        db.session.add(meeting)
        db.session.commit()
        return redirect(url_for('meetings'))
    return render_template('create_meeting.html')

@app.route('/meetings')
@login_required
def meetings():
    meetings = Meeting.query.all()
    return render_template('meetings.html', meetings=meetings)

@app.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        name = request.form.get('name')
        date = datetime.strptime(request.form.get('date'), '%Y-%m-%dT%H:%M')
        description = request.form.get('description')
        event = Event(name=name, date=date, description=description, creator_id=current_user.id)
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('events'))
    return render_template('create_event.html')

@app.route('/events')
@login_required
def events():
    events = Event.query.all()
    return render_template('events.html', events=events)

@app.route('/chat/<event_id>')
@login_required
def chat(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('chat.html', event=event)

@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)
