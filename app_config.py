import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DEBUG = True
SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/test.db"
DATABASE_CONNECT_OPTIONS = {}
SQLALCHEMY_TRACK_MODIFICATIONS = False
THREADS_PER_PAGE = 2
CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secret'
SECRET_KEY = 'secret'
