from flask import Blueprint, request, jsonify, session

from flask import Blueprint, render_template, request, session, jsonify
from models import db
#from flask import Blueprint, request, jsonify, session, render_template

#auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# 这里放登录、logout、注册、loginPage 接口
#@auth_bp.route("/login", methods=["POST"])
#def login():
#    ...
#auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# 登录接口...

#@auth_bp.route("/userPage")
#def user_page():
 #   return render_template("user.html")

# route_modules/auth.py
from flask import Blueprint

print("==== auth.py 被加载执行了 ====")

auth_bp_file = Blueprint("auth_file", __name__, url_prefix="/api/authfile")

@auth_bp_file.route("/test")
def test():
    return "✅ auth蓝图成功加载！"

@auth_bp_file.route("/userPage")
def user_page():
    return "✅ userPage 路由正常"
