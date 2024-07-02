import pymysql
from flask import request, jsonify

def get_connection():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            db="testdb",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print("Connection Error:", e)
        return None

# 註冊會員
def register_user():
    data = request.form
    username = data['username']
    password = data['password']
    permission = data['permission']

    conn = get_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            # 检查用户名是否已存在
            cursor.execute("SELECT COUNT(*) AS count FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result and result['count'] > 0:
                return jsonify({'error': 'Username already exists'}), 400

            # 插入新用户信息
            cursor.execute("INSERT INTO users (username, password, permission) VALUES (%s, %s, %s)",
                           (username, password, permission))
            conn.commit()
    finally:
        conn.close()

    return jsonify({'success': True}), 200

# 用户登录
def login_user():
    data = request.json if request.is_json else request.form
    username = data['username']
    password = data['password']

    conn = get_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cursor:
            # 登录逻辑
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
    finally:
        conn.close()

    if user:
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

def get_user_by_id(user_id):
    conn = get_connection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def get_user_by_username_and_password(username, password):
    conn = get_connection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            return cursor.fetchone()
    finally:
        conn.close()

def update_user_info(user_id, password, permission=None):
    conn = get_connection()
    if conn is None:
        return False
    try:
        with conn.cursor() as cursor:
            if permission is not None:
                # 更新密码和权限
                cursor.execute("""
                    UPDATE users 
                    SET password = %s, permission = %s 
                    WHERE id = %s
                """, (password, permission, user_id))
            else:
                # 只更新密码
                cursor.execute("""
                    UPDATE users 
                    SET password = %s
                    WHERE id = %s
                """, (password, user_id))
            conn.commit()
    finally:
        conn.close()
    return True

# echart相关函数
def query_db(query, args=()):
    conn = get_connection()
    if conn is None:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            return cursor.fetchall()
    finally:
        conn.close()