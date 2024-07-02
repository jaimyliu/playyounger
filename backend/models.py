from flask_login import UserMixin
from backend.utils.db2 import get_user_by_username_and_password, get_user_by_id

class User(UserMixin):
    def __init__(self, id, username=None):
        self.id = id
        self.username = username

    @classmethod
    def authenticate(cls, username, password):
        # 在這裡實現用戶名和密碼的驗證邏輯，如果驗證成功，則返回 User 對象
        user_info = get_user_by_username_and_password(username, password)
        if user_info:
            return cls(id=user_info['id'], username=user_info['username'])
        else:
            return None

def load_user(user_id):
    # 在這裡實現根據 user_id 加載用戶的邏輯
    user_info = get_user_by_id(user_id)
    if user_info:
        return User(id=user_info['id'], username=user_info['username'])
    else:
        return None

