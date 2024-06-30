from flask import Blueprint, render_template, redirect, url_for, session, current_app, request, flash
from app import app, db, socketio
from app.models import User, Meeting, Event
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import send
from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash
# # from app.forms import RegistrationForm
# from flask_oauthlib.client import OAuth
# import requests
# from app import db, login_manager



@app.route('/')
@login_required
def index():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(email=email)
        new_user.set_password(password)  # Hash the password before saving
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)  # Log in the user
            return redirect(url_for('index'))  # Redirect to home page after login

        flash('Invalid email or password')  # Display error message
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required 
def logout():
    logout_user() 

    flash('You have been logged out successfully.', 'success')

    return redirect(url_for('index'))

@app.route('/events')
@login_required
def events():
    events = Event.query.all()
    return render_template('events.html', events=events)


@app.route('/add_event', methods=['POST'])
@login_required
def add_event():
    name = request.form['name']
    date = request.form['date']
    description = request.form['description']
    event = Event(name=name, date=date, description=description, creator_id=current_user.id)
    db.session.add(event)
    db.session.commit()
    return redirect(url_for('events'))


@app.route('/meetings')
@login_required
def meetings():
    meetings = Meeting.query.all()
    return render_template('meetings.html', meetings=meetings)

@app.route('/add_meeting', methods=['GET', 'POST'])
@login_required
def add_meeting():
    if request.method == 'POST':
        location = request.form['location']
        time = datetime.strptime(request.form['time'], '%Y-%m-%dT%H:%M')
        google_meet_link = request.form['google_meet_link']
        user_emails = request.form['user_emails'].split(',')
        
        meeting = Meeting(location=location, time=time, google_meet_link=google_meet_link, creator_id=current_user.id)
        
        for email in user_emails:
            user = User.query.filter_by(email=email.strip()).first()
            if user:
                meeting.users.append(user)
        
        db.session.add(meeting)
        db.session.commit()
        
        flash('Meeting added successfully!', 'success')
        return redirect(url_for('main.meetings'))
    
    return render_template('add_meeting.html')

@app.route('/homies')
@login_required
def homies():
    return render_template('homies.html', homies=current_user.homies)

@app.route('/add_homie', methods=['GET', 'POST'])
@login_required
def add_homie():
    if request.method == 'POST':
        email = request.form.get('email')
        homie = User.query.filter_by(email=email).first()
        if homie and homie != current_user:
            current_user.homies.append(homie)
            db.session.commit()
            flash('Homie added successfully!', 'success')
        else:
            flash('Homie not found or already added!', 'danger')
        return redirect(url_for('main.add_homie'))
    return render_template('add_homie.html')


@app.route('/chat/<event_id>')
@login_required
def chat(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('chat.html', event=event)



@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)
