#PythonApplication_mangeSys/
#├── routes/
#│   ├── __init__.py   # 空文件，新建
#│   ├── auth.py       # 登录、退出、注册
#│   ├── user.py       # ✅【这段代码粘贴到这里】用户管理全部接口
#│   ├── customer.py   # 客户管理
#│   └── escort.py     # 押运人员 
#
#
#
# route_user.py
from flask import Blueprint, request, jsonify

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

@user_bp.route("/list", methods=["GET"])
def user_list():
    # ✅ 第一行就导入！
    from models import User
    from utils import require_permission

    # 权限校验
    if not require_permission("user:list"):
        return jsonify({"code":403, "msg":"无权限"}), 403

    page = request.args.get("page", 1, type=int)
   # ✅ 改成读取 limit，默认10
    page_size = request.args.get("limit", 10, type=int)
    keyword = request.args.get("keyword", "", type=str).strip()

    query = User.query
    if keyword:
        query = query.filter(User.username.like(f"%{keyword}%"))

    paginate = query.paginate(page=page, per_page=page_size, error_out=False)
    user_list = []
    for u in paginate.items:
        user_list.append({
            "id": u.id,
            "username": u.username
        })

    # ✅ Layui 固定格式：code=0，data，count
    return jsonify({
        "code": 0,
        "data": user_list,
        "count": paginate.total
    })
@user_bp.route("/page")
def user_page():
    from flask import render_template
    return render_template("user.html")

#你加一个**临时调试接口**，访问一下自动新增 100 条测试用户，专门用来测试分页、搜索，用完记得删掉这个接口！
@user_bp.route("/add_test_user")
def add_test_user():
    from models import User
    from app import db
    import random
    # 批量生成100条
    for i in range(1,101):
        uname = f"user_{i:03d}"
        # 避免重复，先判断是否存在
        exist = User.query.filter_by(username=uname).first()
        if not exist:
            u = User()
            u.username = uname
            u.password = "123456"
            db.session.add(u)
    db.session.commit()
    return "✅ 100条测试用户添加完成，去刷新用户管理页面！"
    ###2026.10.3
    ##蓝图前缀：`user_bp`，一般注册的时候是 `url_prefix="/user"`
    ####所以接口完整地址：`/user/add`   新增人员


@user_bp.route("/add",methods=["post"])
def user_add():
    from app import db
    from models import User
        # 接收表单提交（form表单，不是json
    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role")
    phone = request.form.get("phone")
    status = request.form.get("status")
    u = User()
    u.username = username
    u.password = password
    u.role = role
    u.phone = phone
    u.status = status
    db.session.add(u)
    db.session.commit()

    return jsonify({"code": 0, "msg": "新增成功"})