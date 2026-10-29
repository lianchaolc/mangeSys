# -*- coding: utf-8 -*-
# 导入Flask核心类
import logging
from flask import Flask
# 从models模块导入sqlalchemy的db对象（数据库实例）
from models import db
# 导入配置文件（里面放数据库地址、密钥等配置）
import config
# 从routes模块导入蓝图对象api_bp，存放所有接口路由
from routes import api_bp
from page import page_bp   # ← 导入page蓝图，写在这里
import traceback
from flask import Flask, jsonify
# 从models模块导入sqlalchemy的db对象（数据库实例）
from models import db
# 导入配置文件（里面放数据库地址、密钥等配置）
import config
# 从routes模块导入蓝图对象api_bp，存放所有接口路由
from routes import api_bp
from page import page_bp   # ← 导入page蓝图，写在这里
# werkzeug 里面的请求异常，用来捕获400/401/403/405
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, MethodNotAllowed
import logging
#`after_request_func` 里面用到了 `request`，但是**没有导入 request**。
from flask import request
#配置简单日志(生产环境用文件日志)
logging.basicConfig(level=logging.ERROR)
# api_bp 在你的api文件中

from modules.business import bp as business_bp


from flask import Flask
from models import db
from routes import auth_bp,api_bp
# 来自 auth.py（你刚改好的这套）
from route_modules.auth import auth_bp_file


from route_modules.route_user import user_bp
# 2. 第二步：导入模型（models里面的User、Role等）
from models import User, Role, Permission, Customer, Escort
def create_app():
   # """
   # 应用工厂函数（Flask标准写法）
  #  好处：可以多次创建app实例、方便单元测试、解耦
   # """
    # 实例化Flask应用
    app = Flask(__name__)

    # session加密密钥，必须配置
    app.secret_key = "supersecretkey123456"
# 读取数据库配置
    app.config.from_pyfile("config.py")

     # 开启打印执行的SQL语句，开发环境打开，上线删掉
    app.config["SQLALCHEMY_ECHO"] = True
    db.init_app(app)



   # 配置数据库连接地址，使用sqlite，数据库文件在instance/crm.db
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/crm.db'
# 关闭模型修改追踪，避免无用警告和额外性能开销
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 从config配置类加载项目全部配置
    # 比如：SQLALCHEMY_DATABASE_URI、SECRET_KEY等
    app.config.from_object(config)

    # 将db数据库实例绑定到当前flask app
    # 早期写法可以直接db = SQLAlchemy(app)，工厂模式下用init_app延迟初始化
    

    # 注册蓝图，把api下面所有路由交给app管理
    app.register_blueprint(api_bp)
    app.register_blueprint(page_bp)  # 页面路由，不带前缀
    # 返回组装好的app实例
    #modle 类
    app.register_blueprint(business_bp)

    app.register_blueprint(auth_bp)


    app.register_blueprint(user_bp)  # 用户蓝图在这里注册
    app.register_blueprint(auth_bp_file)
 
# 404状态码处理器：访问不存在的路由/接口时触发
# 属于HTTP状态捕获，不是代码抛出的Exception异常，和上面全局兜底是两套独立逻辑
    @app.errorhandler(404)
    def not_found(e):
    # 接口不存在，不需要操作数据库，不用rollback
        return jsonify({
        "code":404,
        "msg":"not find servces",
        "data":None
        }),404


    # 400 请求参数错误
    @app.errorhandler(BadRequest)
    def bad_request_handler(e):
        return jsonify({
        "code":400,
        "msg":"Invalid request parameters (request error)",
        "data":None
      }),400


  
    # UnicodeDecodeError 文件编码报错（你当前要解决的）
    @app.errorhandler(UnicodeDecodeError)
    def unicode_decode_err_handler(e):
        err_stack = traceback.format_exc()
        logging.error(f"【编码解码失败】position={e.start}, raw_bytes={e.object[:20].hex()}\n{err_stack}")
        db.session.rollback()
        return jsonify({
            "code": 400,
            "msg": "文件编码错误，请使用UTF-8/GB18030文件",
            "data": None
        }), 400
      

    # @app.errorhandler(Exception)
    # def global_exception_handler(e):
    # 发生异常，回滚数据库会话，防止后续数据库操作卡住
     #    db.session.rollback()
    # 打印异常信息，方便开发时排查问题，生产环境建议替换为logging日志
     #    print(f"error: {e}")
    # 返回统一JSON响应，前端固定解析code/msg/data，不把原始报错信息暴露给用户
     #    return jsonify({
     #    "code": 500,
     #    "msg": "servces error",
    #     "data": None
      #    }), 500

    @app.after_request
    def after_request_func(response):
        #打印请求路径，打印方法
        
         # 示例：获取token
        # token = request.headers.get("Authorization")
        # if not token:
        #     return jsonify({"code":401,"msg":"未登录","data":None}),401
         print(f"request请求:{request.method} {request.path}")
         response.headers["Access-Control-Allow-Origin"] = "*"
         response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
         response.headers["Access-Control-Allow-Headers"] = "*"
    # 必须返回 response！！
         return response
     #from werkzeug.exceptions import MethodNotAllowed

    #@app.errorhandler(MethodNotAllowed)
    #def handle_405(e):
   #     return jsonify({
     #       "code":405,
    #        "msg":"请求方法不允许",
     #       "data":None
     #   }),405







    return app
# 调用工厂函数，创建app实例
app = create_app()
#全局异常处理# 全局兜底异常处理器：捕获所有没有单独处理的未知异常（代码bug、数据库意外报错等）
# 作用：防止Flask返回默认HTML报错页面，统一返回JSON格式；数据库异常时回滚会话，避免会话锁死

@app.route("/api/auth/userPage")
def tmp_userpage():
    return "临时路由能访问！"


if __name__ == "__main__":
    # app.app_context()：Flask应用上下文
    # 数据库操作（create_all、查询）必须在上下文里面执行，否则报错
    with app.app_context():
        # 根据models里面定义的数据库模型，自动创建数据表（不存在才创建，不会覆盖已有表）
        db.create_all()

    # 启动内置开发服务器
    # debug=True：开发模式，代码改动自动重启、页面显示报错详情；线上一定要关掉debug
    app.run(debug=True)
   




 