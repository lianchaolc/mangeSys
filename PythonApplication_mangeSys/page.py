# -*- coding: utf-8 -*-

# 从flask框架导入蓝图、模板渲染函数
from flask import Blueprint, render_template


# 创建一个名叫 page 的蓝图实例，__name__代表当前模块（page.py）
# 蓝图用来统一管理页面相关路由，和接口路由api_bp分开，解耦
page_bp = Blueprint("page", __name__)

# 给这个蓝图注册路由：访问 /customer 会触发这个函数
@page_bp.route("/customer")
def customer_page():
    # render_template：读取 templates 文件夹里的html文件并返回给浏览器
    # templates是Flask默认固定的模板文件夹名称，不用额外配置路径
    return render_template("customer.html")
