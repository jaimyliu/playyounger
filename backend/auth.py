from flask import Blueprint, request, redirect, url_for
from flask_login import login_user, logout_user, login_required
from models import User

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # 這裡應該驗證用戶名和密碼
        user = User(username) # 假設登入成功
        login_user(user)
        return redirect(url_for('frontend.index'))
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('frontend.index'))
