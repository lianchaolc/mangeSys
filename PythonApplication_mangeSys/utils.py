
# utils.py 工具公共函数文件
# 存放项目通用工具：统一接口返回、通用处理函数
import re
from flask import jsonify
#权限装饰器（核心！接口拦截）新建工具文件 `utils.py`
from functools import wraps
from flask import session, jsonify
def check_phone(phone):
    pattern = r'^1[3-9]\d{9}$'
    if re.match(pattern, phone):
        return True
    return False

#接口成功统一返回函数
    #:param data: 需要返回给前端的数据，默认为None，没有数据就不传
    #:param msg: 成功提示文本，默认“操作成功”
    #:return: json响应对象，固定格式 {code, msg, data}
    #code=0 代表业务逻辑执行成功
def resp_ok(data=None,msg="操作成功"):
    return jsonify({
        "code": 0,       # 业务状态码：0=成功
        "msg": msg,      # 提示信息，给页面弹窗展示
        "data": data     # 真实业务数据，列表/对象/None
    })

  
  #  接口业务失败统一返回函数
   # :param msg: 失败原因描述，给前端弹窗展示
  #  :return: json响应对象，固定格式 {code, msg, data}
   # code=1 代表业务逻辑失败（参数错误、重复数据、找不到记录等）
    
def resp_fail(msg="操作失败"):
   
    return jsonify({
        "code": 1,       # 业务状态码：1=业务失败
        "msg": msg,      # 错误提示文本
        "data": None     # 失败情况下一般没有返回数据
    })




#权限代码
def require_permission(perm_key):
    """
    @require_permission("customer:delete")
    接口装饰器，校验是否拥有某个权限
    """
    def decorator(f):
        @wraps(f)
        def inner(*args,**kwargs):
            # 1 判断是否登录
            user_id = session.get("user_id")
            if not user_id:
                return jsonify({"code":401,"msg":"请先登录"})
            # 2 获取登录用户拥有的权限集合（登录的时候存入session）
            user_perms = session.get("permissions",set())
            # 超级管理员特殊判断，如果是admin角色直接放行
            if "admin" in user_perms:
                return f(*args,**kwargs)
            # 判断是否拥有该权限
            if perm_key not in user_perms:
                return jsonify({"code":403,"msg":"权限不足，禁止访问"})
            return f(*args,**kwargs)
        return inner
    return decorator