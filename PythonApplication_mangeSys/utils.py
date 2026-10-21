
# utils.py 工具公共函数文件
# 存放项目通用工具：统一接口返回、通用处理函数
import re
from flask import jsonify
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