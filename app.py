from flask import Flask, render_template
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, create_tables

load_dotenv()

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    create_tables()

from routes import *

if __name__ == '__main__':
    app.run(debug=True, threaded=True)