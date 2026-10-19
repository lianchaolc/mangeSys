#项目根目录
#├─ app.py
#└─ modules/
#   └─ business.py  ←✅ 业务路由放这里（蓝图文件）
#└─ templates/
 #  ├─ base.html
#   └─ customer.html
from flask import Blueprint,render_template
bp = Blueprint("business", __name__,url_prefix="/business")

@bp.route('/customer')
def customer():
    breadcrumb_list = [
        {"title":"首页","url":"/dashboard"},
        {"title":"库存业务","url":""},
        {"title":"抵质押品库存","url":""},
    ]
    print("=====进入customer路由=====", breadcrumb_list)
    return render_template('customer.html', breadcrumb_list=breadcrumb_list)
