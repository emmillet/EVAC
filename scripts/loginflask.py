from flask import Flask
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask.ext.login import current_user
from flask.ext.login import login_required
from flask.ext.login import LoginManager

app = Flask(__name__)

login_manager = LoginManager()
login_manager.setup_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/<name>')
def index(name):
    return '<h1>Hello? {}</h1>'.format(name)