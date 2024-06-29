from app import app, socketio, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)

# from app import create_app, db
# from app.models import User

# app = create_app()

# if __name__ == '__main__':
#     app.run(debug=True)
