# 从app模块导入工厂函数 create_app
from app import create_app
#从models中导入数据库实例实例db
from models import db
# 调用工厂函数，组装得到flask app对象
app=create_app()
# 手动推入app上下文，只有在上下文里面才能操作数据库\

with app.app_context():
    # 创建所有数据表：表不存在就创建；已经存在，不会重复创建，安全
    db.create_all()
    # ========= 初始化测试数据，已经注释，项目启动不会自动插入用户 =========
    # u1 = User(username="admin", real_name="管理员", phone="13800138000")
    # u2 = User(username="test01", real_name="测试用户", phone="13900139000")
    # db.session.add_all([u1, u2])
    # db.session.commit()

# 程序入口，只有直接运行这个文件的时候才启动服务
if __name__ == '__main__':
    # debug=True 开启调试模式：代码修改自动重启、报错页面展示详情
    app.run(debug=True)


