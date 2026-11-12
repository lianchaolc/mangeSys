# 网点的路由 2026.11.12
from flask import Blueprint,render_template,request,redirect,url_for,flash
from models import db, OrgNew
org_bp = Blueprint('org', __name__, url_prefix='/netpoint')

# 网点列表
@org_bp.route('')
def index():
  # 第1步：先查询并赋值（必须放在最前面）
    org_list = OrgNew.query.all()
    # 第2步：再打印调试信息
    print("===", len(org_list))
    for o in org_list:
        print(o.branch_code, o.name)
    # 第3步：返回你写好表头的 org.html 模板
    #return render_template("org.html", org_list=org_list)
    return render_template("netpointorg.html", org_list=org_list)