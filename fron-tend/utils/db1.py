import pymysql
from flask import request, jsonify
from frontend.utils.models import User 

def get_db_connection():
    return pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    db="testdb",  # 替換成你的數據庫名稱
    charset='utf8mb4',  # 推薦使用 'utf8mb4' 編碼
    cursorclass=pymysql.cursors.DictCursor
)


# 將這部分代碼從login.py移動到auth.py中
def register_user():
    db = get_db_connection()
    try:
        data = request.form
        username = data['username']
        password = data['password']
        gender = data['gender']
        region = data['region']
        age = data['age']
        
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM login WHERE username = %s", (username,))
            if cursor.fetchone()['count'] > 0:
                return jsonify({'error': 'Username already exists'}), 400
            
            cursor.execute("INSERT INTO login (username, password, gender, region, age) VALUES (%s, %s, %s, %s, %s)",
                           (username, password, gender, region, age))
            db.commit()
        return jsonify({'success': True}), 200
    except pymysql.MySQLError as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()




def login_user():
    db = get_db_connection()
    try:
        data = request.json if request.is_json else request.form
        username = data['username']
        password = data['password']
        
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM login WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
        
        if user:
        # 登入成功
        # 這裡假設已經有了處理登入後的視圖函數，例如 frontend.index
            return jsonify({'success': True}), 200
        else:
            # 登入失敗
            return jsonify({'error': 'Invalid username or password'}), 401
    finally:
        db.close()
    
# 獲取astray遊戲紀錄
def get_astray_data():
    # 這裡呼叫 get_db_connection() 來取得新的資料庫連接
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM astray ORDER BY level DESC, time ASC")
            results = cursor.fetchall()
        return results
    finally:
        db.close()



def get_user_by_id(user_id):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM login WHERE id = %s", (user_id,))
            return cursor.fetchone()
    finally:
        db.close()

def update_user_info(user_id, password, gender, region, age):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("""
                UPDATE login SET password = %s, gender = %s, region = %s, age = %s WHERE id = %s
            """, (password, gender, region, age, user_id))
            db.commit()
    finally:
        db.close()

# 需要一個取得使用者的函數
def get_user(username, password):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM login WHERE username = %s AND password = %s", (username, password))
            result = cursor.fetchone()
        
        if result:
            return User(id=result['id'], username=result['username'], gender=result['gender'], region=result['region'], age=result['age'])
        return None
    finally:
        db.close()
    

# 這個函數應該傳回所有可能的地區列表
def get_all_regions():
    return ['臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市','新竹縣', '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣' ,'屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣', '基隆市', '新竹市', '嘉義市']


def save_game_data_to_db(username, level, total_time_spent):
    # 將毫秒轉換為秒
    total_time_spent_seconds = total_time_spent / 1000.0

    # 取得資料庫連接
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            # 首先從 login 表取得 region 和 age
            cursor.execute("SELECT region, age FROM login WHERE username = %s", (username,))
            user_info = cursor.fetchone()
            region = user_info['region']
            age = user_info['age']

            # 插入資料到 astray 表
            cursor.execute("""
            INSERT INTO astray (username, level, time, region, age)
            VALUES (%s, %s, %s, %s, %s)
            """, (username, level, total_time_spent_seconds, region, age))
            db.commit()
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        db.rollback()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

# 獲取根據地區和年齡篩選後的數據
def get_filtered_astray_data(region, age):
    db = get_db_connection()
    with db.cursor() as cursor:
        query = "SELECT * FROM astray WHERE 1=1"
        params = []

        if region:
            query += " AND region = %s"
            params.append(region)

        if age:
            query += " AND age = %s"
            params.append(age)

        cursor.execute(query, params)
        results = cursor.fetchall()

    db.close()
    return results


#  remind相關語法
def add_remind_data(username, date_time, remind_time, food):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            # 插入資料到 remind 的內容
            cursor.execute("""
            INSERT INTO remind (username, date_time, remind_time, food)
            VALUES (%s, %s, %s, %s)
            """, (username, date_time, remind_time, food))
            db.commit()
        return True
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        db.rollback()
        return False
    finally:
        db.close()
# 修改 remind 表的資訊
def update_remind_data(username, date_time, remind_time, food):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            # 更新 remind 表中的數據
            cursor.execute("""
            UPDATE remind
            SET date_time = %s, remind_time = %s, food = %s
            WHERE username = %s
            """, (date_time, remind_time, food, username))
            db.commit()
        return True
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        db.rollback()
        return False
    finally:
        db.close()
# 獲取用戶的數據
def get_remind_data_by_username(username):
    db = get_db_connection()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM remind WHERE username = %s", (username,))
            remind_data = cursor.fetchone()
        return remind_data
    finally:
        db.close()