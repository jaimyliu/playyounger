from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_socketio import SocketIO, emit
from frontend.views import frontend_bp
from backend.views import backend_bp
from threading import Thread
from flask import send_from_directory,render_template
from flask import redirect
import schedule
import time
from gemini_0413 import gemini_response
import datetime
import conn_db
from flask import session
from flask import jsonify,current_app
from frontend.views import frontend_bp
from socketio2.views import socketio_bp, socketio


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # 設置應用程序的密鑰

# 設置靜態資料夾路徑
app.static_folder = 'static'

# 初始化登錄管理器
login_manager = LoginManager()
login_manager.init_app(app)

# 設置登錄視圖
login_manager.login_view = 'frontend.login'  

# 註冊前端和後端藍圖
app.register_blueprint(frontend_bp)
app.register_blueprint(backend_bp, url_prefix='/backend')
app.register_blueprint(socketio_bp)

socketio = SocketIO(app)

        
# 設置首頁路由，重定向到前端首頁
@app.route('/')
def index():
    return redirect(url_for('frontend.index'))


# 加載用戶函數
from backend.models import User  
from frontend.utils.models import User 
from frontend.utils.db1 import get_user

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id=user_id)
 
if __name__ == '__main__':
    socketio.run(app, debug=True)
