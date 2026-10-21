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
api_bp = Blueprint("api", __name__, url_prefix="/api")
# 1. 【重点】先创建app实例，不然会报app未定义
app = Flask(__name__)
import re

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
def customer_list_api():
    # 获取url参数，给默认值
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("pageSize", 10, type=int)

    # paginate：SQLAlchemy自带分页
    pagination = Customer.query.order_by(Customer.create_time.desc()).paginate(
        page=page,
        per_page=page_size,
        error_out=False  # page超过最大页数时，不抛异常，返回空
    )
    result = []
    for cus in pagination.items:
        result.append(cus.to_dict())

    return jsonify({
        "code": 200,
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
def  del_cutomer(cid):
# cid = 7，来自url里面的数字
    customer = Customer.query.get(cid)
    if not customer:
        return jsonify({"msg": "客户不存在"}),404
    db.session.delete(customer)
    db.session.commit()
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
