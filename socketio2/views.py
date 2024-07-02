from flask import Blueprint
from flask_socketio import SocketIO
from flask import Flask
app = Flask(__name__)
socketio_bp = Blueprint('socketio', __name__)
socketio = SocketIO(app)