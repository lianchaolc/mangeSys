# 网点的路由 2026.11.12
from flask import Blueprint,render_template,request,redirect,url_for,flash
from models import db, OrgNew
from flask import Blueprint, request, jsonify
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



#

from flask import request, jsonify
from datetime import datetime
# from models import db, OrgNew

@org_bp.route('/netpointadd', methods=['POST'])
def add_netpoint():
    # 1. 获取前端通过 JSON 格式传来的数据
    # silent=True 表示如果前端传来的不是合法的 JSON 格式，不会直接抛出 400 错误，而是返回 None
    data = request.get_json(silent=True)
    
    print("================add_netpoint================")
    # 2. 校验是否收到了有效数据，如果没有收到，直接返回 400 错误
    if not data:
        return jsonify({"code": 1, "msg": "No valid data received."}), 400

    # 3. 获取网点编号，用于后续的唯一性校验
    branch_code = data.get('branch_code')
    
    # 4. 唯一性校验：去数据库里查一下，这个网点编号是不是已经存在了
    # 因为你的 OrgNew 模型里规定了 branch_code 为 unique=True，如果重复插入会引发数据库异常
    if OrgNew.query.filter_by(branch_code=branch_code).first():
        # 如果查到了记录，说明编号已存在，直接拦截，不执行后面的入库操作
        return jsonify({"code": 1, "msg": f"Branch code [{branch_code}] already exists!"}), 200

    # 5. 开始实例化模型并接收所有字段，执行存入数据库的操作
    try:
        # 通过接收到的 data 字典，将各个字段赋值给 OrgNew 模型实例
        new_org = OrgNew(
            branch_code=branch_code,                             # 网点编号
            name=data.get('name'),                               # 网点名称
            branch_type=data.get('branch_type'),                 # 网点类型 (1银行网点，2自助点，3金库)
            region=data.get('region', ''),                       # 所属区域，前端没传则默认空字符串
            address=data.get('address', ''),                     # 详细地址，前端没传则默认空字符串
            status=data.get('status', 1),                        # 状态，前端没传则默认为 1 (启用)
            remark=data.get('remark', ''),                       # 备注信息，前端没传则默认空字符串
            # 经纬度如果没有做地图选点，先默认 None
            longitude=data.get('longitude', None),               # 经度
            latitude=data.get('latitude', None)                  # 纬度
            # create_time 字段不需要传，模型定义里写了 default=datetime.now，数据库会自动生成当前时间
        )
        
        # 6. 将新创建的模型对象添加到 SQLAlchemy 的数据库会话中
        db.session.add(new_org)
        
        # 7. 提交事务，将数据正式写入数据库
        db.session.commit()
        print("================add_netpoint2================")
        # 8. 写入成功，返回成功状态码和英文提示
        return jsonify({"code": 0, "msg": "Saved successfully!"}), 200

    except Exception as e:
        # 9. 如果写入数据库过程中发生了任何异常（比如字段超长、数据库断开连接等）
        # 必须回滚事务，防止数据库连接池被卡死
        db.session.rollback()
        
        # 使用 repr(e) 防止终端打印包含中文的异常信息时引发 UnicodeEncodeError 编码错误
        print("Database error:", repr(e))
        
        # 返回 500 服务器错误，并给出英文提示
        return jsonify({"code": 1, "msg": "Save failed due to database error."}), 500



# =========================================================================
# Batch Test Interface
# =========================================================================
import random
from datetime import datetime

@org_bp.route('/netpointbatch', methods=['GET'])
def batch_add_netpoints():
    regions = ['East', 'West', 'South', 'North', 'Center']
    types = [1, 2, 3]
    
    success_count = 0

    try:
        timestamp = int(datetime.now().timestamp())
        
        for i in range(1, 101):
            code = f"TEST-{timestamp}-{i:03d}"
            
            new_org = OrgNew(
                branch_code=code,
                name=f"Auto_Test_Branch_{i}",
                branch_type=random.choice(types),
                region=random.choice(regions),
                address=f"Test_Avenue_No_{i}",
                status=random.choice([1, 0]),
                remark=f"Batch_Generated_Data_{i}",
                longitude=None,
                latitude=None
            )
            db.session.add(new_org)
            success_count += 1

        db.session.commit()
        return jsonify({
            "code": 0, 
            "msg": f"Batch insert success. Total: {success_count}"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"code": 1, "msg": str(e)}), 500

    #前后端分离的代码
    # =========================================================================
# 获取网点 JSON 数据（前后端分离专用）
# =========================================================================
@org_bp.route('/netpointlist', methods=['GET'])
def get_netpoint_list():
    try:
        # 1. 查询所有网点
        orgs = OrgNew.query.all()
        
        # 2. 将数据库对象转为字典
        result = []
        for org in orgs:
            result.append({
                "branch_code": org.branch_code,
                "name": org.name,
                "branch_type": org.branch_type,
                "region": org.region,
                "address": org.address,
                "status": org.status,
                "remark": org.remark,
                "create_time": org.create_time.strftime('%Y-%m-%d %H:%M:%S') if org.create_time else '',
                "longitude": org.longitude,
                "latitude": org.latitude
            })
            
        # 3. 返回 JSON
        return jsonify({
            "code": 0,
            "msg": "success",
            "data": result
        }), 200
        
    except Exception as e:
        print("Query error:", repr(e))
        return jsonify({"code": 1, "msg": "Database query failed"}), 500
@org_bp.route('/netpointupdate', methods=['POST'])
def update_netpoint():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"code": 1, "msg": "No data received."}), 400
        
    branch_code = data.get('branch_code')
    
    # 1. 根据编号查询数据库
    org = OrgNew.query.filter_by(branch_code=branch_code).first()
    if not org:
        return jsonify({"code": 1, "msg": "Branch not found."}), 404
        
    try:
        # 2. 更新其他允许修改的字段（编号不修改）
        org.name = data.get('name', org.name)
        org.branch_type = data.get('branch_type', org.branch_type)
        org.region = data.get('region', org.region)
        org.address = data.get('address', org.address)
        org.status = data.get('status', org.status)
        org.remark = data.get('remark', org.remark)
        
        db.session.commit()
        return jsonify({"code": 0, "msg": "Update successfully!"}), 200
        
    except Exception as e:
        db.session.rollback()
        print("Update error:", repr(e))
        return jsonify({"code": 1, "msg": "Update failed due to database error."}), 500     
     #删除代码



@org_bp.route('/netpointdelete', methods=['POST'])
def delete_netpoint():
    data = request.get_json(silent=True)
    if not data or not data.get('branch_code'):
        return jsonify({"code": 1, "msg": "No branch_code received."}), 400
        
    branch_code = data.get('branch_code')
    
    try:
        # 1. 去数据库里找这条数据
        org = OrgNew.query.filter_by(branch_code=branch_code).first()
        if not org:
            return jsonify({"code": 1, "msg": "Branch not found."}), 404
            
        # 2. 从会话中删除并提交
        db.session.delete(org)
        db.session.commit()
        
        return jsonify({"code": 0, "msg": "Delete successfully!"}), 200
        
    except Exception as e:
        db.session.rollback()
        print("Delete error:", repr(e))
        return jsonify({"code": 1, "msg": "Delete failed due to database error."}), 500