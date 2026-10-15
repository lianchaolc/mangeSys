# 导入os模块，用来处理文件路径
import os

# __file__：当前这个 config.py 文件的完整路径
# os.path.dirname(__file__)：拿到 config.py 所在的文件夹路径
# os.path.abspath：把路径转为绝对路径（完整路径）
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 数据库连接地址
# sqlite:/// 代表使用sqlite数据库
# os.path.join(BASE_DIR, 'instance', 'crm.db') 拼接路径：项目根目录/instance/crm.db
# crm.db 就是存放客户数据的数据库文件
SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'crm.db')}"
#放心！**这行代码不用改盘符**，它自动适配你的 D 盘路径，不会去找 F 盘。

# 关闭SQLAlchemy的对象修改追踪功能
# 这个功能会消耗额外性能，一般开发里都关掉，不影响我们增删改查
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 密钥，Flask内部用来做加密、签名，比如后面做登录、token会用到
# 随便写一串复杂字符串就行，不要泄露给别人
SECRET_KEY = "crm-api-2026-secret"
