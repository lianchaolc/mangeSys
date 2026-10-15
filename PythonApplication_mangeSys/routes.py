from flask import Blueprint, jsonify, request
from models import Customer
from models import db
api_bp = Blueprint("api", __name__, url_prefix="/api")

# 查询客户列表
@api_bp.route("/customer/list", methods=["GET"])
def customer_list():
    cus_list = Customer.query.all()
    result = []
    for cus in cus_list:
        d = cus.to_dict()
        result.append(d)
    return jsonify({"code": 200, "data": result})

# 新增客户
@api_bp.route("/customer/add", methods=["POST"])
def customer_add():
    data = request.get_json()
    if not data:
        return jsonify({"code":400, "msg":"Invalid JSON"}), 400
    new_cus = Customer(
        name=data.get("name"),
        phone=data.get("phone"),
        email=data.get("email"),
        address=data.get("address"),
        level=data.get("level", "normal_customer")
    )
    db.session.add(new_cus)
    db.session.commit()
    return jsonify({"code":200, "msg":"Success"}), 200
