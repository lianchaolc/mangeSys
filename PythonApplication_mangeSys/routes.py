from email.policy import default
from operator import methodcaller
from flask import Blueprint, jsonify, request
from sqlalchemy.event import api
from models import Customer
from models import db
from flask import Blueprint, jsonify, request, render_template
from flask import Flask, render_template, jsonify
# 导入我们封装好的统一返回工具

from models import db, Customer
# 导入我们封装好的统一返回工具
from utils import resp_ok, resp_fail



from flask import Blueprint, request, jsonify, session
from models import User   # 导入用户模型
from datetime import datetime
from flask import jsonify
from models import db, Permission, Role, User
from functools import wraps
auth_bp = Blueprint("auth",__name__,url_prefix="/api/auth")
api_bp = Blueprint("api", __name__, url_prefix="/api")
# 1. 【重点】先创建app实例，不然会报app未定义
app = Flask(__name__)
import re
import bcrypt




#验证 session 里面权限到底存的是什么（定位权限问题根源）
def require_perm(perm_key):
    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            perms = session.get("permissions", [])
            user_id = session.get("user_id")
            if not user_id:
                return jsonify({"code":401,"msg":"未登录"})
            # admin超级用户直接放行
            if "admin" in perms:
                return f(*args, **kwargs)
            if perm_key not in perms:
                return jsonify({"code":403,"msg":"没有操作权限"})
            return f(*args,**kwargs)
        return inner
    return decorator
#




# 查询客户列表
#@api_bp.route("/customer/list", methods=["GET"])
#def customer_list():
 #   cus_list = Customer.query.all()
 #   result = []
#    for cus in cus_list:
#        d = cus.to_dict()
 #       result.append(d)
 #   return jsonify({"code": 200, "data": result})
 #   
 #   
@api_bp.route("/customer/list", methods=["GET"])
@require_perm("customer:list")
def customer_list_api():
    #后端防护
    # 最小页码强制=1
# 还可以拿到总页数，超过最大页就自动变成最后一页
   
    # 获取url参数，给默认值
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("pageSize", 10, type=int)
    page=max(page,1)
    page_size = max(page_size, 1)
  # 分页查询
    pagination = Customer.query.paginate(page=page, per_page=page_size, error_out=False)
    records = pagination.items
    total = pagination.total
    result = []
    for cus in pagination.items:
        result.append(cus.to_dict())

    return jsonify({
        "code": 0,
        "data": result,
        "total": pagination.total,       # 总条数
        "page": page,
        "pageSize": page_size,
        "pages": pagination.pages         # 总页数
    })

# 新增客户
@api_bp.route("/customer/add", methods=["POST"])
def customer_add():
    data = request.get_json()

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    address = data.get("address", "").strip()
    email = data.get("email", "").strip()  # 新增接收邮箱
    # ========== 正则校验手机号 ==========
    pattern = r"^1[3-9]\d{9}$"
    if not re.fullmatch(pattern, phone):
        return {"msg": "手机号格式不正确！"}, 400
    # ==================================
    address = data.get("address", "").strip()
    # 校验姓名非空
    if not name:
        return {"msg": "姓名不能为空"},400

    exist = Customer.query.filter_by(phone=phone).first()
    if exist:
        return {"msg": "手机号重复"}, 400

    if not data:
        return jsonify({"code":400, "msg":"Invalid JSON"}), 400
    # 邮箱校验
    if email and "@" not in email:
        return resp_fail("邮箱格式不正确")
    

  #  if exist:
    #    # 提前拦截，返回json，不会触发数据库异常
     #   return jsonify({"code": 400, "msg": "phone alearly，can add！"})
  #  new_cus = Customer(
   #     name=data.get("name"),
  #      phone=data.get("phone"),
   #     email=data.get("email"),
  #      address=data.get("address"),
  #      level=data.get("level", "normal_customer")
   # )
  #  db.session.add(new_cus)
  #  db.session.commit()
  #  return jsonify({"code":200, "msg":"Success"}), 200



# 后端校验是安全防线，前端校验可以被抓包绕过，这里必须校验
    if not name or len(name) < 2 or len(name) > 10:
        # 参数不合法，直接返回失败，return之后后面代码不再执行
        return resp_fail("姓名必须2‑10个字符")

    # 手机号校验：不为空、全部数字、长度11位、1开头
    if not phone or not phone.isdigit() or len(phone) != 11 or not phone.startswith("1"):
        return resp_fail("手机号格式错误，请输入1开头11位手机号")

 

    # 地址非空，最大长度60字符
    if not address or len(address) > 60:
       return resp_fail("地址不能为空且不能超过60字符")
    # ======================后端参数校验结束======================
    # 所有校验全部通过，才执行数据库新增
    new_customer = Customer(
        name=name,
        phone=phone,
        email=email,
        address=address
    )
    db.session.add(new_customer)   # 添加到会话
    db.session.commit()            # 提交保存到数据库

    # 新增成功，调用统一成功返回
    return resp_ok(msg="客户新增成功!!!!!!")

@api_bp.route("/customer/edit", methods=["POST"])
def customer_edit():
    data = request.get_json()
    if not data:
        return resp_fail("无效JSON参数")

    cid = data.get("id")
    if not cid:
        return resp_fail("缺少客户id")

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    address = data.get("address", "").strip()
    email = data.get("email", "").strip()

    # 姓名校验 和新增保持一致
    if not name or len(name) < 2 or len(name) > 10:
        return resp_fail("姓名必须2‑10个字符")

    # 手机号正则校验 和新增保持一致
    pattern = r"^1[3-9]\d{9}$"
    if not re.fullmatch(pattern, phone):
        return resp_fail("手机号格式错误，请输入1开头11位手机号")

    # 根据自增id查询客户
    cust = Customer.query.get(cid)
    if not cust:
        return resp_fail("该客户不存在")

    # 手机号重复校验：排除当前这条自己
    exist = Customer.query.filter(Customer.phone == phone, Customer.id != cid).first()
    if exist:
        return resp_fail("手机号重复")

    # 赋值更新
    cust.name = name
    cust.phone = phone
    cust.address = address
    cust.email = email

    db.session.commit()
    return resp_ok(msg="客户修改成功")



















# 1、返回HTML页面（浏览器直接打开看表格页面）
@api_bp.route('/customer_list')
def customer_list_page():
    page=request.args.get("page",1, type=int)
    page_size = 10
    pagination = Customer.query.order_by(Customer.create_time.desc()).paginate(
        page=page,
        per_page=page_size,
        error_out=False
    )
    # pagination.items 是当前页数据

    return render_template("customer_list.html", pagination=pagination)


#3  html 删除数据
@api_bp.route('/customer/<int:cid>', methods=["DELETE"])
@require_perm("customer:delete")
def  del_cutomer(cid):
# cid = 7，来自url里面的数字
    customer = Customer.query.get(cid)
    if not customer:
        return jsonify({"msg": "客户不存在"}),404
    db.session.delete(customer)
    db.session.commit()
    print("当前用户权限：", session.get("permissions"))
    return jsonify({"msg":"删除成功"}),200

    return render_template("customer_list.html", pagination=pagination)

from flask import jsonify

# ========== 【新增：仪表盘看板接口，单独加在下面】 ==========
# ✅ 页面路由（主app，无/api，访问 /dashboard 打开网页）
#@app.route("/dashboard")
#def dashboard_page():
#    return render_template("dashboard.html")

# ✅ 统计接口路由（放在 api_bp 蓝图里，自动带 /api 前缀，地址：/api/dashboard/stats）
#@api_bp.route("/dashboard/stats")
#def dashboard_stats():
 #   mock_data = {
##        "totalStock": 128,
 #       "todayIn": 45,
  #      "todayOut": 32,
 #       "todoTask": 7,
 #       "trend": {
 #           "xdata": ["周一","周二","周三","周四","周五"],
 #           "ydata": [12, 22, 18, 28, 25]
  #      },
#        "pieData": [
#            {"name":"A网点","value":40},
#            {"name":"B网点","value":30},
#            {"name":"C网点","value":20},
#            {"name":"其他","value":10}
 #       ]
 #   }
#    return {"code":0, "data": mock_data, "msg":"ok"}

# ✅页面路由（主app，负责渲染html）
@app.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")

# ✅接口路由（蓝图，只负责json，地址 /api/dashboard/stats）
@api_bp.route("/dashboard/stats")
def dashboard_stats():
    mock_data = {
        "totalStock": 128,
        "todayIn": 45,
        "todayOut": 32,
        "todoTask": 7,
        "trend": {
            "xdata": ["周一","周二","周三","周四","周五"],
            "ydata": [12, 22, 18, 28, 25]
        },
        "pieData": [
            {"name":"A网点","value":40},
            {"name":"B网点","value":30},
            {"name":"C网点","value":20},
            {"name":"其他","value":10}
        ]
    }
    return {"code":0, "data": mock_data, "msg":"ok"}

# GET 查询单条：最终地址 /api/customer/<cid>
# GET 查询单条
@api_bp.route("/customer/<int:cid>", methods=["GET"])
def customer_info(cid):
    """
    获取单条客户详情（修改弹窗回填用）
    """
    print("customer_info")
    cus = Customer.query.get(cid)
    if not cus:
        return {"code": -1, "msg": "客户不存在"}
    try:
        data = cus.to_dict()
        return {"code": 0, "data": data}
    except Exception as e:
        print("customer_info 报错", e)
        return {"code": -1, "msg": "数据转换失败"}

    ...

# PUT 更新
@api_bp.route("/customer/<int:cid>", methods=["PUT"])
def customer_update(cid):
    try:
        data = request.get_json()
        print("收到前端数据：", data)
        cus = Customer.query.get(cid)
        if not cus:
            return {"code": -1, "msg": "客户不存在"}
        cus.name = data.get("name")
        cus.phone = data.get("phone")
        cus.email = data.get("email")
        cus.address = data.get("address")
        db.session.commit()
        print("customer_update修改成功，commit完成")
        return {"code": 0, "msg": "修改成功"}
    except Exception as e:
        db.session.rollback()
        print("更新报错！", str(e))
        return {"code": -1, "msg": "更新失败:" + str(e)}







# 登录相关蓝图，也可以直接写在api_bp里面，看你项目
auth_bp = Blueprint("auth", __name__,url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    用户登录接口
    登录成功：1.校验账号密码；2.把user_id、用户权限集合存入session
    session保存在服务端，后续权限装饰器从session读取权限
    """
    # 1.接收前端提交账号密码
    json_data = request.get_json()
    username = json_data.get("username", "").strip()
    password = json_data.get("password", "").strip()

    # 简单非空校验
    if not username or not password:
        return jsonify({"code": 400, "msg": "用户名和密码不能为空"})

    # 2.数据库查询用户
    user = User.query.filter_by(username=username).first()
    # 注意：真实项目密码要加密，这里demo简化判断
    if not user or user.password != password:
        return jsonify({"code": 400, "msg": "用户名或者密码错误"})
    perm_keys = [p.perm_key for r in user.roles for p in r.permissions]
    session["permissions"] = perm_keys
    # 3.登录成功！写入session（服务端保存）
    session["user_id"] = user.id      # 当前登录用户id

    # ✅调用模型方法get_perms()获取该用户所有权限标识集合 {customer:list, customer:add...}
    # 权限集合存入session，后续 @require_permission 装饰器直接读取，不用每次查数据库
    # 遍历多个角色，收集权限
    perm_keys = []
    for role in user.roles:
        for p in role.permissions:
            perm_keys.append(p.perm_key)

    session["permissions"] = perm_keys
    # ============加上这两行打印！！============
    print(f"user_id: {session.get('user_id')}")
    print(f"permissions: {session.get('permissions')}")
    # ========================================

    return jsonify({"code": 0, "msg": "登录成功"})


@auth_bp.route("/loginout", methods=["GET"])
def logout():
    """退出登录，清空session"""
    session.clear()


    print("我退出登陆")
    return jsonify({"code": 200, "msg": "已退出登录"})




# 只执行一次初始化超级管理员
#@auth_bp.route("/init_rbac",methods=["GET"])
#def init_rbac():
 #   """初始化权限、角色、超级管理员，只调用一次！"""
 #   try:
        # 先判断是否已经存在admin账号，避免重复创建报错
   #     exist_admin = User.query.filter_by(username="admin").first()
    #    if exist_admin:
    #        return jsonify({"code": -1, "msg": "已经初始化过了，不要重复调用！"})

        # 1.创建权限标识
    #    p1 = Permission(perm_key="customer:list",perm_name="查看客户列表")
    #    p2 = Permission(perm_key="customer:add",perm_name="新增客户")
    #    p3 = Permission(perm_key="customer:edit",perm_name="修改客户")
    #    p4 = Permission(perm_key="customer:delete",perm_name="删除客户")
        # admin特殊标识，放行全部权限
   #     p_admin = Permission(perm_key="admin",perm_name="超级管理员权限")

        # 2.创建admin角色，绑定全部权限
    #    role_admin = Role(role_name="超级管理员",remark="拥有全部功能权限")
     #   role_admin.permissions = [p1,p2,p3,p4,p_admin]

        # 3.创建普通业务员角色（只能查看、新增）
      #  role_staff = Role(role_name="业务员",remark="仅查看、新增客户")
    #    role_staff.permissions = [p1,p2]

        # 4.创建管理员账号
    #   admin_user = User(username="admin",password="123456")
   #     admin_user.roles = [role_admin]

     #   db.session.add_all([p1,p2,p3,p4,p_admin,role_admin,role_staff,admin_user])
   #     db.session.commit()
    #    return jsonify({"code":0,"msg":"RBAC初始化成功！账号admin，密码123456"})
  #  except Exception as e:
 #       db.session.rollback()
     #   return jsonify({"code":-1,"msg":f"初始化失败：{str(e)}"})
#routes.py 加路由，用来渲染登录页面（放在 auth_bp 里）
@auth_bp.route("/loginPage")
def login_page():
    return render_template("login.html")
@api_bp.route("/customer")
def customer_page():
    # 这个路由负责渲染templates里的customer.html模板
    return render_template("customer.html")



####  2026.10.26

#- 路由：`/register` 渲染注册页面
#- 接口：`/api/auth/register` 提交注册
#pip install flask-sqlalchemy bcrypt 先安装依赖（如果没装）



# ========== 【新增：注册页面路由】 访问 /register 打开注册html页面 ==========
@auth_bp.route('/register', methods=["GET"])
def register_page():
    print("进入注册页面")
    return render_template("register.html")

# ========== 【新增：注册提交接口，和登录接口配套 /api/auth/register】 ==========
@auth_bp.route("/register", methods=["POST"])
def api_register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    print("进入注册野提交数据")
    # 1. 参数校验
    if not username or not password:
        return jsonify({"code": 1, "msg": "账号和密码不能为空"})
    if len(username) < 3:
        return jsonify({"code": 1, "msg": "账号至少3个字符"})
    if len(password) < 4:
        return jsonify({"code": 1, "msg": "密码至少4个字符"})

    # 2. 判断账号是否已经存在
    exist_user = User.query.filter_by(username=username).first()
    if exist_user:
        return jsonify({"code": 1, "msg": "该账号已经被注册"})

    # 3. 密码哈希加密（重点！数据库不存明文密码）
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    pwd_hash = bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

    # 4. 写入数据库
    new_user = User(username=username, password=pwd_hash)
    db.session.add(new_user)
    db.session.commit()

    # 5. 返回成功，code=0 和登录保持统一
    return jsonify({"code": 0, "msg": "注册成功！请去登录"})