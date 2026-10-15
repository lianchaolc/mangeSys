目名称：简易客户管理系统（CRM 本地版，命令行）
实后台本质就是：实体（客户、用户）、增删改查、参数校验、异常、配置、日志，很多后台业务逻辑就是这套思路，只是线上换成 web。
大量用到你刚学的：`class`、`__init__`、实例属性、`hasattr/getattr/setattr/delattr`。

#### 业务需求

1. 实体：客户 Customer（id, name, phone, email, level【VIP / 普通】, create_time）
2. 功能：
   - 添加客户（校验手机号格式、邮箱格式，不能为空）
   - 查询客户（按 id / 姓名模糊搜索）
   - 修改客户信息（动态修改对象属性，正好用 `setattr`）
   - 删除客户（`delattr`）
   - 列出全部客户
   - 数据持久化：保存到 json 文件（模拟数据库）
   - 日志：操作日志（什么时候谁新增 / 删除客户）
   - 异常捕获：输入非法、id 不存在、json 损坏不直接崩程序
3. 项目目录（**重点！真实项目绝对不写一个 py**）

```
crm/
├── config.py          # 配置：文件路径、日志级别（线上项目都有配置文件）
├── models.py          # 模型类 Customer 写在这里！你的__init__、实体类放这里
├── service.py         # 业务层：增删改查逻辑（和model分离，分层思想）
├── utils.py           # 工具：日志、手机号校验函数
├── main.py            # 入口：命令行交互菜单
├── data/
│   └── customer.json  # 存储数据
├── requirements.txt   # 依赖（就算只用内置库也要写，规范）
└── README.md          # 怎么运行、功能说明
```

✅ 可以刻意用上你刚学的知识点：

- `Customer` 类里面 `__init__` 初始化属性
- 修改客户信息时：用 `hasattr` 判断属性、`setattr` 修改、`getattr`读取
- 练习异常 try-except、日志 logging（线上必备）

> 
> 做完这个，你就懂了后端经典三层思想：模型 (model) → 业务 (service) → 入口 (main)，后面转 Flask/Django 非常顺滑。










#####贰

### `pip install -r requirements.txt` 拆开讲

1. **pip**：Python 自带的包管理工具，专门用来安装、卸载第三方库（Flask、Flask-SQLAlchemy 都属于第三方库，Python 原生没有）
2. **install**：就是【安装】的意思
3. **-r**：参数，英文 `read`，代表**读取后面这个文件**
4. **requirements.txt**：我们之前建好的清单文件，里面写了项目需要哪些包、版本

👉 整句翻译：**读取 requirements.txt 里面的清单，自动把清单上所有库一次性全部安装**

#### 对比理解

如果不写这条命令，你就要分开敲两次：

```
pip install Flask==2.3.3
pip install Flask-SQLAlchemy==3.1.1
```

用 `-r` 一条命令搞定，项目里包越多，越省事。

#### 补充两点（贴合咱们这个 CRM 项目）

- 这个命令是在 **PowerShell / CMD 终端** 里面跑的，不是写到 py 代码里！
- 以后你换一台电脑、拷贝代码走，只要带上 `requirements.txt`，跑这一行，环境就和现在一模一样，不会出现 “在我电脑能跑，你电脑缺包报错”。

#### 小提示





保留文件

"""
# 从 flask_sqlalchemy 导入数据库ORM工具
# ORM：不用手写SQL语句，用Python类和对象就能操作数据库
from flask_sqlalchemy import SQLAlchemy
# 导入时间模块，用来自动记录创建时间
from datetime import datetime

# 创建一个数据库操作对象db，后面增删改查都靠它
db = SQLAlchemy()

# 定义客户模型类，继承 db.Model，代表这是一张数据库表
class Customer(db.Model):
    # __tablename__：指定这张表在数据库里的名字，叫 customer
    __tablename__ = "customer"

    # id：整数类型，主键（唯一标识一条数据），自动递增
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # name：字符串，最多50个字，nullable=False → 不允许为空，必须填名字
    name = db.Column(db.String(50), nullable=False)
    # phone：字符串最多20字符，unique=True → 手机号不能重复，nullable=False 必填
    phone = db.Column(db.String(20), unique=True, nullable=False)
    # email：邮箱，字符串50字符，可以为空
    email = db.Column(db.String(50))
    # address：地址，最多100字符，可以为空
    address = db.Column(db.String(100))
    # level：客户等级，默认值是 "普通客户"，不传参数就自动填这个
    level = db.Column(db.String(20), default="普通客户")
    # create_time：创建时间，default=datetime.now → 添加这条数据的时候，自动记录当前时间
    create_time = db.Column(db.DateTime, default=datetime.now)

    # __init__ 构造函数：新建一个客户对象的时候，用来接收参数赋值
    def __init__(self, name, phone, email, address, level="普通客户"):
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.level = level

    # to_dict() 自定义方法：把数据库取出来的【客户对象】转换成字典
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "level": self.level,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
"""""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50))
    address = db.Column(db.String(100))
    # 这里我暂时不用中文，直接写英文，绕开Windows粘贴中文编码灾难
    level = db.Column(db.String(20), default="normal_customer")
    create_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, name, phone, email, address, level="normal_customer"):
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.level = level

    def to_dict(self):
        # 在to_dict里面把英文转成中文输出给接口，数据库存英文，源码无中文，彻底杜绝报错
        display_level = "普通客户" if self.level == "normal_customer" else self.level
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "level": display_level,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
        }
伍 
**ask 是 Python 的轻量 Web 框架**
`Blueprint`、`jsonify`、`request` 是 Flask 里三个高频组件，用来写后端接口（给前端 / 别的程序调用，返回 JSON）。

> 
> 对比你之前学的：Go 的 Iris / Gin，和 Flask 干的是一类事：接收 HTTP 请求、处理逻辑、返回响应。

```
from flask import Blueprint, jsonify, request
```

## 逐个解释
# 一句话

**Flask 是 Python 的轻量 Web 框架**
`Blueprint`、`jsonify`、`request` 是 Flask 里三个高频组件，用来写后端接口（给前端 / 别的程序调用，返回 JSON）。

> 
> 对比你之前学的：Go 的 Iris / Gin，和 Flask 干的是一类事：接收 HTTP 请求、处理逻辑、返回响应。

```
from flask import Blueprint, jsonify, request
```

## 逐个解释

### 1. `request`

接收前端发过来的请求数据。
前端 GET/POST 传的参数、json、header、表单，都从 `request` 拿。

```
# 获取post的json数据
data = request.get_json()
# 获取url上 ?name=xxx 的参数
name = request.args.get("name")
```

### 2. `jsonify()`

快速构造**JSON 响应**，自动设置 `Content-Type: application/json`，后端接口最常用。

```
# 直接返回json给前端
return jsonify(code=200, msg="success", data={"count":10})
```

如果你自己用 `json.dumps`，还要手动设置响应头，`jsonify` 帮你封装好了。

### 3. `Blueprint`（蓝图，重点）

**模块化拆分接口**。
一个项目接口多了之后，不能全部堆在一个 `app.py` 里面。
Blueprint 相当于**子路由模块**：

- 比如：user 蓝图（用户登录、注册）、file 蓝图（文件上传、文本统计）
- 每个蓝图单独写在一个 py 文件，最后统一注册到主 app 上
- 可以统一加路由前缀，例如 `/api/user`

示例：

```
# 新建一个蓝图，前缀 /api/file
file_bp = Blueprint("file", __name__, url_prefix="/api/file")

@file_bp.route("/stat", methods=["POST"])
def file_stat():
    # 拿到前端传的文件参数，调用你之前写的文本统计逻辑
    req_data = request.get_json()
    return jsonify(code=200, data={})
```

主程序里：

```
app.register_blueprint(file_bp)
```

## 整体场景串起来（结合你之前的文本统计工具）

你可以把你写好的 `TextAnalyzer` 类，包在 Flask 接口里：
前端发一个 POST 请求，传文件路径或者文本内容 → Flask 接收 → 调用你的统计代码 → `jsonify` 返回统计结果给前端。
👉 这就是简单的后端服务！

## 和你之前学习路线的关系

你现在顺序：Python 基础 → 文件 IO、OOP 类 → **然后就是 Flask（Web 接口）**，正好接上。

## 补充区分（笔记版）

- Flask：Web 框架，用来写 HTTP 服务
- Blueprint：模块拆分，大型项目解耦
- request：读请求（入参）
- jsonify：输出 JSON 响应（返回）

### 小 demo，直接跑看效果


陆
1. **应用工厂 `create_app()`**
这是 Flask 项目规范结构，适合蓝图拆分、多环境配置，正式项目都这么写，不直接 `app=Flask(__name__)` 然后全局写路由。
2. `db.init_app(app)`
延迟绑定。因为 db 在 models 里提前定义了，那时候还没有 app，后面工厂函数里面再绑定。
3. **上下文 app.app_context ()**
Flask 很多组件（数据库）是依附 app 上下文运行的；不在路由函数里直接操作数据库，就需要手动 with 上下文。
4. `db.create_all()`
⚠️ 只新建表，**不会更新表结构**；模型改字段之后这个方法没用，后续要学 Alembic 做数据库迁移。




柒
# 一句话

**Python 虚拟环境（venv）：给你这个 Flask 项目单独隔离的一套 Python + 包，不和电脑全局的包混在一起。**
你截图里是 PyCharm 检测到项目里有 `requirements.txt`，提示你新建虚拟环境。

## 1、先讲痛点（为什么必须有它）

假设你电脑全局装了：`flask==2.2`
但是这个管理系统项目，需要 `flask==3.0`

- 如果直接全局升级 flask，你别的旧项目就会直接崩（版本冲突）
- 虚拟环境就是**隔离沙盒**：每个项目自己一套依赖，互不打扰。

## 2、两个配套文件一起理解：`venv` + `requirements.txt`

1. **venv（虚拟环境文件夹）**
里面单独拷贝一份 Python 解释器，这个项目 pip 安装的包，**只装在这个 venv 里面，不进系统全局**。
激活这个环境之后：pip、python 命令都优先走这个隔离环境。
2. **requirements.txt（依赖清单）**
记录这个项目需要哪些包、什么版本，示例内容：

```
flask==3.0.0
flask-sqlalchemy==3.1.1
```

别人拿到你的代码，只要执行：

```
pip install -r requirements.txt
```

就能一键装好一模一样的依赖。

> 
> 截图提示就是：PyCharm 发现了你这个清单文件，问你要不要自动创建 venv、自动安装里面的包。

## 3、常用命令（Windows）

```
# 1. 创建虚拟环境，名字一般叫 venv
python -m venv venv

# 2. 激活虚拟环境（PowerShell）
venv\Scripts\Activate.ps1
# cmd里：venv\Scripts\activate.bat

# 激活成功，前面会出现 (venv) 标记
# 然后安装依赖
pip install -r requirements.txt

# 退出虚拟环境
deactivate
```

> 
> 激活之后，你 pip 装的 flask、sqlalchemy 全部安装到 `venv/Lib/site-packages`，不是全局。

## 4、PyCharm 里这个提示怎么选？

弹窗：`检测到requirements.txt，创建虚拟环境`
✅ 推荐：直接点创建，PyCharm 自动帮你：

1. 在项目生成 venv 文件夹
2. 自动激活
3. 自动执行 `pip install -r requirements.txt`
4. 自动把这个 venv 设置成本项目的 Python 解释器

⚠️ 注意：`.venv` / `venv` 文件夹**不要提交到 git**，只提交 requirements.txt！

## 5、笔记精简版（写到 note）

- 虚拟环境：项目隔离容器，解决包版本冲突，**每个项目独立一套依赖**
- requirements.txt：依赖快照，用来同步、部署、给别人复现环境
- 开发规范：**所有 Python 项目都必须用虚拟环境，禁止直接往全局 pip 装包**

## 6、和你现在 Flask 项目的关系

你这个 Flask+SQLAlchemy 蓝图项目，以后部署到服务器，流程就是：

1. 服务器新建 venv
2. `pip install -r requirements.txt`
3. 启动项目

### 补充小坑

- 不激活 venv 的时候，pip 装包装到全局，项目环境乱掉
- 换电脑、换服务器，只需要代码 + requirements.txt，不用拷贝 venv 文件夹（很大）

要不要我给你写生成 requirements.txt 的命令？就是你写好项目之后，导出依赖清单。


一句话：**这个 `env` 虚拟环境，只属于当前这个 `PythonApplication_mangeSys` 项目，别的新项目完全不受它影响。**

拆开讲清楚：

1. **隔离范围**
它就是这个文件夹里独立的一套 Python + 依赖包，只在你打开这个管理系统项目、选中这个 env 解释器的时候生效。
你之后新建另一个 Python 项目：

- 需要**单独再创建一个新的虚拟环境**（新的 `venv` / `env`）
- 新项目自己装 flask、其他包，和这个 mangeSys 的 env 互不干扰