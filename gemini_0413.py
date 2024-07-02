import google.generativeai as genai
import os
from dotenv import load_dotenv
import datetime
import time

# 安裝pip install google-generativeai 需要用管理員權限開啟cmd後再安裝

load_dotenv(".env")
# api_key = os.getenv('Gemini_API_KEY')
api_key = ""
genai.configure(api_key = api_key)

def gemini_response(text):
    # 調用模型
    model = genai.GenerativeModel('gemini-pro')
    #找尋歷史對話紀錄以方便延續對話
    chat = model.start_chat(history=[])
    # 對話的接續,使用chat.send_message函式執行
    response = chat.send_message(f"你是提醒助理,請依據這個框裡的資料:[{text}],提醒使用者該吃藥以及吃什麼藥,回答語言為繁體中文,回答格式:['現在時間,早上八點十分','描述提醒使用者吃藥的話語藥品名稱'],無法判斷藥品名稱時把接收到的藥品名稱填進格式的'食物名稱'欄位後,其餘的部分照格式回答,無法回答請回復:無法回答或是無法判斷")
    return response.text


# 設定要觸發的小時和分鐘
def set_alarm(target_hour, target_minute):
    """ 設定鬧鐘，並在達到指定時間時觸發提醒。 """
    triggered = False
    while True:
        now = datetime.datetime.now()
        # 檢查是否達到設定的時間，且未觸發提醒
        if now.hour == target_hour and now.minute == target_minute and not triggered:
            # 觸發提醒
            response = gemini_response(now)
            print(response)
            triggered = True
        elif now.minute != target_minute:
            # 重置觸發狀態
            triggered = False
        time.sleep(1)

# print(api_key)
# text = "現在時間18:35,藥品名稱:血壓藥"

# respon = gemini_response(f"{text}")
# print(respon)