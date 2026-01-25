# minimal_test.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'test'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

print("✅ Minimal Flask-SQLAlchemy + Flask-Migrate setup working!")