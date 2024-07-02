import sys
import os
from flask import Flask
from flask_socketio import SocketIO

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# 创建 Flask 应用程序实例
app = Flask(__name__)

# 创建 SocketIO 实例，并将其与应用程序绑定
socketio = SocketIO(app)

# 导入并注册前端蓝图
from frontend.views import frontend_bp
app.register_blueprint(frontend_bp)

# 导入并注册后端蓝图
from flask_game import backend
from .frontend.views import frontend_bp
app.register_blueprint(backend, url_prefix='/backend')