import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key_here_for_development'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///drop4life.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
