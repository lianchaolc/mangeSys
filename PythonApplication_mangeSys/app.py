# -*- coding: utf-8 -*-

# 导入Flask核心类
from flask import Flask
# 从models模块导入sqlalchemy的db对象（数据库实例）
from models import db
# 导入配置文件（里面放数据库地址、密钥等配置）
import config
# 从routes模块导入蓝图对象api_bp，存放所有接口路由
from routes import api_bp


def create_app():
   # """
   # 应用工厂函数（Flask标准写法）
  #  好处：可以多次创建app实例、方便单元测试、解耦
   # """
    # 实例化Flask应用
    app = Flask(__name__)

    # 从config配置类加载项目全部配置
    # 比如：SQLALCHEMY_DATABASE_URI、SECRET_KEY等
    app.config.from_object(config)

    # 将db数据库实例绑定到当前flask app
    # 早期写法可以直接db = SQLAlchemy(app)，工厂模式下用init_app延迟初始化
    db.init_app(app)

    # 注册蓝图，把api下面所有路由交给app管理
    app.register_blueprint(api_bp)

    # 返回组装好的app实例
    return app


# 调用工厂函数，创建app实例
app = create_app()


if __name__ == "__main__":
    # app.app_context()：Flask应用上下文
    # 数据库操作（create_all、查询）必须在上下文里面执行，否则报错
    with app.app_context():
        # 根据models里面定义的数据库模型，自动创建数据表（不存在才创建，不会覆盖已有表）
        db.create_all()

    # 启动内置开发服务器
    # debug=True：开发模式，代码改动自动重启、页面显示报错详情；线上一定要关掉debug
    app.run(debug=True)



 