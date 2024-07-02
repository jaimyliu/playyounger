from flask_login import UserMixin
from flask import Blueprint, render_template, redirect, url_for, request,jsonify,flash
from flask_login import login_required
from flask_login import UserMixin,logout_user, login_required, current_user
from flask_login import login_user as flask_login_user
from flask import send_from_directory,render_template


class User(UserMixin):
    def __init__(self, id, username, gender, region, age):
        self.id = id
        self.username = username
        self.gender = gender
        self.region = region
        self.age = age

    @staticmethod
    def get(user_id):
        from .db1 import get_db_connection
        db = get_db_connection()  # 使用 get_db_connection 函數取得資料庫連接
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM login WHERE id = %s", (user_id,))
            result = cursor.fetchone()
        db.close()  # 確保關閉資料庫連接
        if result:
            return User(id=result['id'], username=result['username'],
                        gender=result['gender'], region=result['region'],
                        age=result['age'])
        return None
    
    # Flask-Login要求這個方法判斷用戶是否被驗證
    def is_authenticated(self):
        return True

    # Flask-Login要求這個方法判斷用戶賬號是否被啟用
    def is_active(self):
        return True

    # Flask-Login要求這個方法判斷用戶賬號是否是匿名
    def is_anonymous(self):
        return False
    
def load_user(user_id):
    from frontend.utils.db1 import get_db_connection
    db = get_db_connection()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM login WHERE id = %s", (user_id,))
        user_record = cursor.fetchone()
    if user_record:
        return User(id=user_record['id'], username=user_record['username'],
                    gender=user_record['gender'], region=user_record['region'], age=user_record['age'])
    return None