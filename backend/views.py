from flask import Blueprint, render_template, redirect, request, session,url_for,flash
from flask_login import UserMixin,  logout_user, login_required, current_user
from flask_login import login_user as backend_login_user
from .utils.errorRespones import errorRespones
import time
from backend.utils.db2 import *
from backend.models import User
from pyecharts.charts import Bar, Line, Pie, Scatter
from pyecharts import options as opts
from collections import defaultdict

backend_bp = Blueprint('backend', __name__, url_prefix='/backend', template_folder='templates')

@backend_bp.route('/login', methods=['GET', 'POST']) 
def login():
    if request.method == 'GET':
        return render_template('login2.html')  # 使用後端模板

    else:
        username = request.form['username']
        password = request.form['password']
        
        # 檢查使用者是否存在並且密碼正確
        user_info = get_user_by_username_and_password(username, password)
        if user_info:
            # 創建用戶對象
            user = User(id=user_info['id'], username=user_info['username'])
            # 登入用戶，這裡是重要的一步
            backend_login_user(user)
            
            # 登入成功，將使用者資訊存儲到 session 中
            session['username'] = username
            session['permission'] = user_info['permission']
            return render_template('index2.html')  # 登入後重定向到後台首頁
        else:
            flash('帳號或密碼錯誤')  # 使用 flash 來回饋錯誤信息
            return render_template('login2.html') 

        

# 這個函數處理註冊表單的提交
@backend_bp.route('/backend_register', methods=['POST'])
def backend_register():
    # 呼叫 register_user() 函數，並傳入 db 參數
    response = register_user()
    
    # Flask的jsonify回應物件提供了一個.get_json()方法，可以直接取得JSON資料
    if response[1] == 200:  
        json_data = response[0].get_json()  # 取得JSON數據
        if json_data.get('success'):
            # 如果註冊成功，則重新導向至首頁
            return render_template('index2.html')
        else:
            # 如果註冊失敗，則顯示錯誤訊息
            return render_template('member2.html', error=json_data.get('error'))
    else:
        # 如果HTTP狀態碼不是200，也顯示錯誤訊息
        return render_template('member2.html', error="An error occurred during registration.")

# 這個函數顯示註冊頁面
@backend_bp.route('/member2.html', methods=['GET'])
def regis():
    # 只需渲染和返回注册页面模板
    return render_template('member2.html')

# 需要一個取得使用者的函數
def get_user(username, password):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        result = cursor.fetchone()
        if result:
            # 提供所有必要的參數給User類別
            user = User(id=result['id'], username=result['username'], permission=result['permission'])
            return user
        return None

# 修改會員資料的頁面
@backend_bp.route('/rewrite2')
@login_required
def rewrite():
    user_info = get_user_by_id(current_user.id)  # 假設 current_user.id 存在且正確
    return render_template('rewrite2.html', user_info=user_info)

# 處理更新用戶資料的請求
@backend_bp.route('/update_user', methods=['POST'])
@login_required
def update_user():
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')
    if password != confirm_password:
        flash("Passwords do not match!")
        return redirect(url_for('backend.rewrite2', user_id=user_id))
    # 對於 user 類型的用戶，不會從表單中獲取 permission，而是使用現有的值
    permission = request.form.get('permission') if 'permission' in request.form else None
    try:
        update_user_info(user_id, password, permission)
        flash("User info updated successfully!")
        return render_template('index2.html')
    except Exception as e:
        flash(str(e))
        return redirect(url_for('backend.rewrite2', user_id=user_id))

# echart相關函式
# ECharts - 时间花费每日
# 新的echart1视图，包含所有图表的入口
@backend_bp.route('/echart1')
def show_echart1():
    # 这里，我们将调用一个生成所有图表的函数，并把所有图表的HTML传递给模板
    # 假设你已经定义了三个函数: generate_time_spent_daily_chart, generate_motion_magnitude_chart, generate_motion_scatter_chart
    # Generate charts
    time_spent_chart = generate_time_spent_daily_chart()
    motion_magnitude_chart = generate_motion_magnitude_chart()
    motion_scatter_chart = generate_motion_scatter_chart()
    most_common_direction = generate_most_common_direction()
    # Pass all charts HTML to the template
    return render_template(
        'echart1.html',
        time_spent_chart=time_spent_chart,
        motion_magnitude_chart=motion_magnitude_chart,
        motion_scatter_chart=motion_scatter_chart,
        most_common_direction=most_common_direction
    )
def generate_time_spent_daily_chart():
    data = query_db("SELECT timestamp FROM sports_data")
    time_list = [str(row['timestamp']) for row in data]
    line = Line()
    line.add_xaxis(time_list)
    line.add_yaxis("用户使用时间", [1] * len(time_list))  # 假定使用时间是 1
    line.set_global_opts(
        xaxis_opts=opts.AxisOpts(name="时间"),
        yaxis_opts=opts.AxisOpts(name="使用时间"),
        title_opts=opts.TitleOpts(title="用戶使用時間分布")
    )
    return line.render_embed()
# ECharts - 运动幅度
def generate_motion_magnitude_chart():
    data = query_db("SELECT roll, pitch, yaw FROM sports_data")
    small_count, medium_count, large_count = 0, 0, 0
    for row in data:
        roll, pitch, yaw = abs(row['roll']), abs(row['pitch']), abs(row['yaw'])
        if 20 < roll < 40 and 20 < pitch < 40 and 20 < yaw < 40:
            small_count += 1
        elif 40 <= roll < 50 and 40 <= pitch < 50 and 40 <= yaw < 50:
            medium_count += 1
        elif roll >= 50 or pitch >= 50 or yaw >= 50:
            large_count += 1
    pie = Pie()
    pie.add("", [("小幅度", small_count), ("中幅度", medium_count), ("大幅度", large_count)])
    pie.set_global_opts(title_opts=opts.TitleOpts(title="肌肉动作强度分布"))
    return pie.render_embed()
# ECharts - 运动幅度散点图
def generate_motion_scatter_chart():
    data = query_db("SELECT timestamp, roll, pitch, yaw FROM sports_data")  # 请替换为您实际的列名
    motion_counts = defaultdict(lambda: {"small": 0, "medium": 0, "large": 0})
    for row in data:
        timestamp = row['timestamp']
        roll, pitch, yaw = abs(row['roll']), abs(row['pitch']), abs(row['yaw'])
        if 20 < roll < 40 and 20 < pitch < 40 and 20 < yaw < 40:
            motion_counts[timestamp]["small"] += 1
        elif 40 <= roll < 50 and 40 <= pitch < 50 and 40 <= yaw < 50:
            motion_counts[timestamp]["medium"] += 1
        elif roll >= 50 or pitch >= 50 or yaw >= 50:
            motion_counts[timestamp]["large"] += 1
    scatter = Scatter()
    scatter.add_xaxis([item for item in motion_counts.keys()])
    scatter.add_yaxis("小幅度", [counts["small"] for counts in motion_counts.values()])
    scatter.add_yaxis("中幅度", [counts["medium"] for counts in motion_counts.values()])
    scatter.add_yaxis("大幅度", [counts["large"] for counts in motion_counts.values()])
    scatter.set_global_opts(
        title_opts=opts.TitleOpts(title="不同运动幅度在时间线上的分布"),
        xaxis_opts=opts.AxisOpts(type_="time", name="时间"),
        yaxis_opts=opts.AxisOpts(name="数量")
    )
    return scatter.render_embed()

    
#最常操作的方向
def generate_most_common_direction():
    data = query_db("SELECT direction FROM sports_data")
    # 统计每种方向出现的次数
    direction_count = {}
    for row in data:
        print(row)
        direction = row['direction']
        direction_count[direction] = direction_count.get(direction, 0) + 1
    # 创建条形图示例
    bar = Bar()
    bar.add_xaxis(list(direction_count.keys()))
    bar.add_yaxis("出现次数", list(direction_count.values()))
    # 将渲染后的 HTML 传递给模板
    return bar.render_embed()
@backend_bp.route('/logout')
@login_required  # 确保只有登录用户能够访问这个路由
def logout():
    logout_user()  # 注销用户
    flash('You have been logged out.')  # 可选：向用户显示一条消息
    return render_template('login2.html')   # 登出後重定向到後台登入頁面


