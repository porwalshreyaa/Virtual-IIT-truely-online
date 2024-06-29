class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///your_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth settings
    GOOGLE_CLIENT_ID = 'your_google_client_id.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = 'your_google_client_secret'
    GOOGLE_DISCOVERY_URL = 'https://accounts.google.com/.well-known/openid-configuration'
