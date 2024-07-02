import pymysql
from flask import request, jsonify
from frontend.utils.models import User 
import logging
from datetime import datetime

def get_db_connection():
    return pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    db="testdb",  # 替換成你的數據庫名稱
    charset='utf8mb4',  # 推薦使用 'utf8mb4' 編碼
    cursorclass=pymysql.cursors.DictCursor
)

def get_med_info(username):
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute('SELECT date_time, remind_time, food FROM remind WHERE username = %s', (username,))
        data = cursor.fetchone()
        if data:
            hour, minute = data["remind_time"].split(':')
            return  hour, minute, data["food"]
        else:
            return None
    finally:
        cursor.close()
        db.close()

def db_save_sports(username , data):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        timestamp = data['timestamp']
        roll = data['roll']
        pitch = data['pitch']
        yaw = data['yaw']
        free_acc_x = data['free_acc_x']
        free_acc_y = data['free_acc_y']
        free_acc_z = data['free_acc_z']
        direction = data['direction']
        print(username)
        print(timestamp)
        print(roll)
        print(pitch)
        print(yaw)
        print(free_acc_x)
        print(free_acc_y)
        print(free_acc_z)
        sql = "INSERT INTO sports_data (username, timestamp, roll, pitch, yaw, free_acc_x, free_acc_y, free_acc_z, direction) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (username, timestamp, roll, pitch, yaw, free_acc_x, free_acc_y, free_acc_z, direction))
        db.commit()
        cursor.close()
        db.close()
        
        logging.info("Inserted data: %s", data)
        logging.info("Executed SQL: %s", sql)
        return '数据已成功保存到数据库'
    except Exception as e:
        # 記錄詳細的錯誤訊息到日誌中
        logging.error("Error saving data to database: %s", repr(e))
        # 傳回包含錯誤訊息的回應和狀態碼 500
        return '保存数据到数据库时出现错误: {}'.format(repr(e)), 500
    # finally:
    #     cursor.close()
    #     db.close()

now = datetime.now()

# # Format the datetime to include hours and minutes in 'HHMM' format
# timestamp = "2024-04-19 18:03:020"

# username = 'Howard'
# data = {"timestamp": timestamp, "roll": 20.2, "pitch": 0.52, "yaw": 0.35, "free_acc_x": 1.9, "free_acc_y": 20.0, "free_acc_z": 2.01,"direction": 5.24}
# db_save_sports(username , data)