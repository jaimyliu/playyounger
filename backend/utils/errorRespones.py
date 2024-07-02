from flask import render_template

def errorRespones(errorMsg):
    return render_template('error.html',errorMsg='發生錯誤')