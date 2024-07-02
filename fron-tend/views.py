from flask import Blueprint, render_template, redirect, url_for, request,jsonify,flash,current_app
from flask_login import login_required
from flask_login import UserMixin,logout_user, login_required, current_user
from flask_login import login_user as flask_login_user
from flask_socketio import emit
from flask_socketio import SocketIO
from flask import send_from_directory,render_template
import subprocess
import os
from flask_cors import CORS
import json
from frontend.utils.db1 import *
import logging
import schedule
import time
from gemini_0413 import gemini_response
import datetime
import conn_db
from flask import session
from flask_socketio import emit
from socketio2.views import socketio_bp, socketio
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
# from concurrent.futures import ThreadPoolExecutor



frontend_bp = Blueprint('frontend', __name__, template_folder='templates')

# executor = ThreadPoolExecutor(max_workers=20)

# 在這裡初始化 CORS，允許跨來源存取前端藍圖中的路由
CORS(frontend_bp)

# 儲存訊息的變數
message = "初始消息"


@frontend_bp.after_request
def add_header(response):
    # Add security policies only for 'antigolf' route
    if 'antigolf' in request.url:
        response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    
    # Add CORS headers
    response.headers['Access-Control-Allow-Origin'] = '*'  # 允許所有網域存取
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'  # 允許的HTTP方法
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'  # 允許的headers訊息
    response.headers['Access-Control-Allow-Credentials'] = 'true'  # 允許cookies

    return response

#  其他頁面處理
@frontend_bp.route('/')
def index():
    return render_template('index.html')
    
@frontend_bp.route('/one_type.html')
def one_type():
    return render_template('one_type.html')

@frontend_bp.route('/double_type.html')
def double_type():
    return render_template('double_type.html')

# 這個函數處理註冊表單的提交
@frontend_bp.route('/register', methods=['POST'])
def register():
    # 呼叫 register_user() 函數，並傳入 db 參數
    response = register_user()
    
    # Flask的jsonify回應物件提供了一個.get_json()方法，可以直接取得JSON資料。
    if response[1] == 200:  # 這裡檢查HTTP狀態碼是否為200
        json_data = response[0].get_json()  # 取得JSON數據
        if json_data.get('success'):
            # 如果註冊成功，則重新導向至首頁
            return redirect(url_for('frontend.login'))
        else:
            # 如果註冊失敗，則顯示錯誤訊息
            return render_template('joing.html', error=json_data.get('error'))
    else:
        # 如果HTTP狀態碼不是200，也顯示錯誤訊息
        return render_template('joing.html', error="An error occurred during registration.")

# 這個函數顯示註冊頁面
@frontend_bp.route('/joing.html', methods=['GET'])
def joing():
    # 只需渲染和返回註冊頁面
    return render_template('joing.html')

@frontend_bp.route('/game_list.html')
def game_list():
    return render_template('game_list.html')

@frontend_bp.route('/member.html')
def member():
    # 只需渲染和返回會員功能列表頁面
    return render_template('member.html')

# 顯示排行榜內容
@frontend_bp.route('/list.html')
def list():
    # 獲取按照 level 降序和 time 升序排序的 astray 數據
    try:
        astray_data = get_astray_data()
    # 將數據傳遞給模板渲染
        return render_template('list.html', astray_data=astray_data)
    except Exception as e:
        current_app.logger.error("Error fetching astray data: %s", str(e))
        flash('Failed to fetch game records.', 'error')
        return render_template('index.html')
# 針對條件顯示排行榜的內容
@frontend_bp.route('/filter_rankings', methods=['POST'])
def filter_rankings():
    data = request.json
    region = data.get('region', '')
    age = data.get('age', '')

    # 呼叫資料庫查詢函數，傳入篩選條件
    filtered_data = get_filtered_astray_data(region, age)
    return jsonify(filtered_data)

# 針對GAI提醒功能的函數
def check_and_alert(username):
    global message
    # 檢查提醒時間
    hour, minute, medicine = conn_db.get_med_info(username)
    print(f"hour:{hour},minute:{minute},food:{medicine}")
    alert_time = {"hour": int(hour), "minute": int(minute), "medicine": medicine}
    now = datetime.datetime.now()
    if now.hour == alert_time['hour'] and now.minute == alert_time['minute']:
        text_to_ai = f"當前時間{now.hour}:{now.minute},藥品名稱:{medicine}."
        text = gemini_response(f"{text_to_ai}")
        message = text
        send_text = {"text":text}
        print(f"----------------AI_respons:{send_text}")
        socketio.emit('gemini',send_text)

def run_schedule(username):
    try:
        if username:
            def schedule_task():
                schedule.every().minute.do(lambda: check_and_alert(username))  # 使用 lambda 來確保正確傳遞 username
                print("schedule run!!!")
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            # 在新线程中启动调度任务
            schedule_thread = Thread(target=schedule_task)
            schedule_thread.daemon = True  # 将线程设置为守护线程，主线程退出时自动结束
            schedule_thread.start()
        else:
            print("Failed to schedule!!!")
    except Exception as e:
        current_app.logger.error(f'Error running schedule: {e}')

# 針對會員登入功能的函數
@frontend_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        from frontend.utils.db1 import get_user
        user = get_user(username, password)
        if user:
            flask_login_user(user, remember=True)
            run_schedule(username)
            # 啟動調度程序
            next_page = request.args.get('next')
            return redirect(next_page or url_for('frontend.index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

# 會員登出功能
@frontend_bp.route('/logout')
@login_required  # 確保只有登入使用者能夠存取這個路由
def logout():
    logout_user()  # 用戶登出
    flash('You have been logged out.')  # 可選擇：向使用者顯示一則訊息
    return redirect(url_for('frontend.login'))  # 重定向到登入頁面



# 需要一個取得使用者的函數
def get_user(username, password):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM login WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()
        if result:
            # 提供所有必要的參數給User類
            user = User(id=result['id'], username=result['username'], gender=result['gender'], region=result['region'], age=result['age'])
            return user
        return None

# 修改會員資料的頁面
@frontend_bp.route('/rewrite')
@login_required
def rewrite():
    user_info = get_user_by_id(current_user.id)  # 假設 current_user.id 存在且正確
    all_regions = get_all_regions()  # 取得所有地區選項
    return render_template('rewrite.html', user_info=user_info, all_regions=all_regions)

# 處理更新用戶資料的請求
@frontend_bp.route('/update_user', methods=['POST'])
@login_required
def update_user():
    password = request.form['password']
    confirm_password = request.form['confirmPassword']
    if password != confirm_password:
        flash("Passwords do not match!")
        return redirect(url_for('frontend.rewrite'))

    gender = request.form['gender']
    region = request.form['region']
    age = request.form['age']
    update_user_info(current_user.id, password, gender, region, age)  # 假設 current_user.id 存在且正確
    flash("User info updated successfully!")
    return redirect(url_for('frontend.index'))


# remind相關功能
@frontend_bp.route('/remind')
@login_required
def remind():
    user_info = get_user_by_id(current_user.id)  # 假設 current_user.id 存在且正確
    return render_template('add_remind.html', user_info=user_info)
# 新增資料至table(remind)
@frontend_bp.route('/add_remind', methods=['POST'])
@login_required
def add_remind():
    username = current_user.username
    date_time = request.form['date_time']
    remind_time = request.form['remind_time']
    food = request.form['food']
    # 呼叫 db1.py 中的函數新增提醒數據
    success = add_remind_data(username, date_time, remind_time, food)
    
    if success:
        flash("提醒添加成功!")
        return redirect(url_for('frontend.index'))
    else:
        flash("添加提醒时发生错误，请稍后重试。")
        return redirect(url_for('frontend.remind'))
    
# 修改remind的資料
@frontend_bp.route('/rewrite_remind', methods=['GET'])
@login_required
def rewrite_remind():
    # 這裡取得目前使用者的 remind 數據
    remind_data = get_remind_data_by_username(current_user.username)
    return render_template('rewrite_remind.html', remind_data=remind_data)
@frontend_bp.route('/update_remind', methods=['POST'])
@login_required
def update_remind():
    date_time = request.form.get('date_time')
    remind_time = request.form.get('remind_time')
    food = request.form.get('food')
    if date_time and remind_time and food:
        # 呼叫 db1.py 中的函數來更新提醒數據，確保傳遞所有四個必需的參數
        success = update_remind_data(current_user.username, date_time, remind_time, food)
        if success:
            flash("提醒更新成功!")
            return redirect(url_for('frontend.index'))
        else:
            flash("更新提醒时发生错误，请稍后重试。")
    else:
        flash("所有字段都是必填项。")
    return redirect(url_for('frontend.rewrite_remind'))

    



# 遊戲相關路由
@frontend_bp.route('/HexGL/')
def HexGL():
    return send_from_directory('frontend/templates/game/HexGL-master', 'game.html')

@frontend_bp.route('/HexGL/<path:filename>')
def HexGL_static(filename):
    return send_from_directory('frontend/templates/game/HexGL-master', filename)

@frontend_bp.route('/ballgame/')
def ballgame():
    return send_from_directory('frontend/templates/game/ballgame', 'ballgame.html')

@frontend_bp.route('/ballgame/<path:filename>')
def ballgame_static(filename):
    return send_from_directory('frontend/templates/game/ballgame', filename)

@frontend_bp.route('/Astray/')
def Astray():
    return send_from_directory('frontend/templates/game/Astray', 'Astray.html')

@frontend_bp.route('/Astray/<path:filename>')
def Astray_static(filename):
    return send_from_directory('frontend/templates/game/Astray', filename)

# 為 遊戲'antigolf' 路由新增特定的headers
@frontend_bp.route('/antigolf/')
def antigolf():
    response = send_from_directory('frontend/templates/game/antigolf', 'antigolf.html')
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    return response

@frontend_bp.route('/antigolf/<path:filename>')
def antigolf_static(filename):
    response = send_from_directory('frontend/templates/game/antigolf', filename)
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    return response


@frontend_bp.route('/flappy_bird/')
def flappy_bird():
    return send_from_directory('frontend/templates/game/flappy_bird', 'index.html')

@frontend_bp.route('/flappy_bird/<path:filename>')
def flappy_bird_static(filename):
    return send_from_directory('frontend/templates/game/flappy_bird', filename)

@frontend_bp.route('/agar/')
def agar():
    return redirect("http://127.0.0.1:3000")

# 儲存遊戲數據
def save_level_time(username, level, total_time_spent):
    save_game_data_to_db(username, level, total_time_spent)
    print(f"Level {level} time saved: {total_time_spent/1000} seconds")

@login_required
@frontend_bp.route('/save-level', methods=['POST'])
def save_level():
    data = request.get_json()
    username = current_user.username
    level = data.get('level')

    if level is not None:
        # 設定預設時間為0
        save_level_time(username, level, 0)
        return jsonify({'success': 'Level saved successfully'}), 200
    else:
        return jsonify({'error': 'Level is required'}), 400

@login_required
@frontend_bp.route('/save-time', methods=['POST'])
def save_time():
    data = request.get_json(force=True)
    username = current_user.username
    total_time_spent = data.get('totalTimeSpent', None)
    level = data.get('level')

    if total_time_spent is not None and level is not None:
        save_level_time(username, level, total_time_spent)
        return jsonify({'success': 'Time saved successfully'}), 200
    else:                                                              
        return jsonify({'error': 'Time spent and level are required'}), 400
    

@login_required
@frontend_bp.route('/save-sports', methods=['POST'])
def save_sports():
    try:
        username = current_user.username

        # 資料庫連線配置
        db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'root',
            'db': 'testdb',
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

        # 建立資料庫連接
        db = pymysql.connect(**db_config)

        data = request.json
        print(data)
        username = current_user.username  # 取得目前使用者的使用者名稱

        with db.cursor() as cursor:
            # 執行資料庫操作
            sql = "INSERT INTO sports_data (username, timestamp, roll, pitch, yaw, free_acc_x, free_acc_y, free_acc_z, direction) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (username, data['timestamp'], data['roll'], data['pitch'], data['yaw'], data['free_acc_x'], data['free_acc_y'], data['free_acc_z'],data['direction']))
            # 列印插入的資料和執行的 SQL 語句
            logging.info("Inserted data: %s", data)
            logging.info("Executed SQL: %s", sql)
        db.commit()

        return '数据已成功保存到数据库'

    except Exception as e:
        # 記錄詳細的錯誤訊息到日誌中
        logging.error("Error saving data to database: %s", repr(e))
        # 傳回包含錯誤訊息的回應和狀態碼 500
        return '保存数据到数据库时出现错误: {}'.format(repr(e)), 500

    finally:
        # 確保資料庫連線已關閉
        if 'db' in locals() and db and db.open:
            cursor.close()
            db.close()


@frontend_bp.route('/message')
def get_message():
    global message
    if message == "初始消息":
        # 返回當前消息的JSON
        return jsonify(message=message)
    else:
        cur_message = message
        message = "初始消息"
        return jsonify(message=cur_message)