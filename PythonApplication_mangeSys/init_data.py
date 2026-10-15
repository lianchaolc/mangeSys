#接下来新建 init_data.py#
#导入app 工厂函数
from app import create_app
#导入数据库对象 ，用户模型
from models import db,User

# 生成app实例
app = create_app()

# 进入flask上下文，才能操作数据库
with app.app_context():
    # 判断admin账号是否已经存在，不存在才新增，避免主键冲突报错
 if not User.query.filter_by(username="admin").first():
        # 构造两条测试用户数据
        u1 = User(username="admin", real_name="管理员", phone="13800138000")
        u2 = User(username="test01", real_name="测试用户", phone="13900139000")
        # 添加到会话
        db.session.add_all([u1, u2])
        # 提交保存到sqlite数据库
        db.session.commit()
        print("✅ 测试用户初始化成功！")
 else:
        print("ℹ️ admin用户已经存在，跳过新增")