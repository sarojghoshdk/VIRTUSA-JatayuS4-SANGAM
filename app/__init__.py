from flask import Flask
from flask_login import LoginManager
from flask_session import Session

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False

    Session(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .routes import register_blueprints
    register_blueprints(app)

    return app
