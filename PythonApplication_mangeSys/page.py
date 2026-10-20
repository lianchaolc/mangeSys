# -*- coding: utf-8 -*-
# flask页面视图模块，页面路由渲染
from flask import Blueprint, render_template

# 创建一个名叫 page 的蓝图实例，__name__代表当前模块，也就是page.py
# 页面路由统一放页面路径，接口路径给api_bp分开管理
page_bp = Blueprint("page", __name__)

@page_bp.route("/dashboard")
def dashboard_page():
 #   """
  #  仪表盘首页看板页面
 #   访问地址:  /dashboard
  #  返回渲染 dashboard.html模板，模板继承layout.html公共母版
  #  """
    return render_template("dashboard.html")

# 注册页面路由，访问 /customer 就进入这个函数
@page_bp.route("/customer")
def customer_page():
    # render_template读取templates文件夹下html文件，返回页面
    # templates是Flask默认模板文件夹，不用额外写路径
    return render_template("customer.html")


@page_bp.route("/test")
def test_page():
    return render_template("test.html")

# 押运人员管理页面
@page_bp.route("/escort")
def escort_page():
    return render_template("escort.html")

# 网点机构管理页面
@page_bp.route("/org")
def org_page():
    return render_template("org.html")


