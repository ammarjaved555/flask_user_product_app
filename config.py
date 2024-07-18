class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/flask_database'
    SQLALCHEMY_TRACK_MODIFICATIONS = False