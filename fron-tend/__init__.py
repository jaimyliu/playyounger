from flask import Flask
from flask_socketio import SocketIO

socketio = None

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    global socketio
    socketio = SocketIO(app)

    from .views import frontend_bp
    app.register_blueprint(frontend_bp)

    return app
