✅ 已经完成：

1. Flask 蓝图拆分 page.py（页面）、routes（接口）
2. Jinja2 模板继承 layout 母版，统一后台布局、顶部导航、侧边菜单跳转 + 自动展开高亮
3. 客户管理页面：前端 JS 完成新增、查询、删除；后端接口完成业务逻辑
4. Git 版本阶段性提交，可以回退版本
5. Layui 后台页面，解决编码、留白、侧边栏各种坑

下面给你**按学习顺序，由浅入深的学习点**，贴合你这个后台项目，直接可以在现有项目上面迭代练习，不用新建项目。

## 第一阶段：完善现有后台（优先做，就在当前项目练）

### 1. 表单后端校验 & 统一返回格式

- 当前：前端做了校验，后端 routes 里面校验比较零散。
- 学习目标：后端必须二次校验（前端校验可以被绕过），封装统一 JSON 返回工具函数。

```
# 示例统一返回
def resp_ok(data=None, msg="成功"):
    return jsonify({"code":0,"msg":msg,"data":data})

def resp_fail(msg="失败"):
    return jsonify({"code":1,"msg":msg})
```

> 
> 所有接口统一返回 `code、msg、data`，前端统一解析。

### 2. 分页功能（重点必学）

现在客户列表是一次性返回全部数据，数据多会卡顿。

- 后端：`limit offset` 分页，接收 page、pageSize 参数
- 前端 Layui 表格分页，改造 `/api/customer/list` 接口
- 练习：SQLAlchemy `paginate()` 使用。


索条件 + 分页联动


### 3. 编辑修改功能

客户管理目前只有新增、删除，缺少编辑。

1. 后端写接口：`GET /api/customer/{id}` 获取单条详情；`PUT /api/customer/{id}` 更新数据
2. 前端：点击编辑弹出 Layui 弹窗，回填表单，提交修改。

### 4. 错误统一处理

- 404 页面：访问不存在路由，跳出自定义 404 页面，而不是 Flask 默认报错页
- 全局异常捕获，接口异常返回友好 json，而不是 500 堆栈。

### 5. 静态文件管理

现在 CDN 引入 layui，练习下载 layui 放到项目`static`文件夹，本地加载，脱离网络也能跑。

## 第二阶段：数据库进阶（SQLAlchemy）

1. **模型关系**：一对多

> 
> 示例：一个网点 (org) 多个押运人员 (escort)；一个客户多个订单。练习外键、relationship。

2. 查询进阶：where 过滤、排序、模糊搜索 `like`
3. 字段默认值、时间自动更新、唯一约束。
4. 数据库迁移工具 Flask‑Migrate（修改表结构不用手动删库重建）。

## 第三阶段：登录权限（真实后台必备）

1. 登录页面 login.html，账号密码登录
2. session 会话保存登录状态，`Flask‑Session`
3. 登录拦截：未登录禁止访问 `/dashboard` `/customer` 所有后台页面，写装饰器 `@login_required`
4. 密码加密存储：**不能明文存密码**，使用 werkzeug 进行密码 hash 加密。
5. 用户角色：管理员 / 普通用户，不同角色看不同菜单。

## 第四阶段：前端增强（Layui）

1. layui layer 弹窗、消息提示、确认框
2. 表单组件、下拉选择框、日期选择器
3. 文件上传：图片 / 附件上传后端保存
4. 确认：把你现在手写的表格，改成 layui-table 组件（自带分页、排序）

## 第五阶段：接口与项目规范

1. 请求方法规范 GET 查询 / POST 新增 / PUT 修改 / DELETE 删除 RESTful 风格
2. request 对象学习：获取 json、表单、url 参数
3. 配置文件拆分：把 SECRET_KEY、数据库地址放到 config.py，不要硬编码写在 app.py
4. 项目目录规范化，区分：配置、模型、接口、页面、静态资源、模板。

## 第六阶段：拓展（选学）

1. 使用 `Flask‑JWT` 令牌登录（前后端分离模式）
2. 日志模块 logging，记录操作日志、错误日志
3. 简单导出 Excel（客户列表导出 excel）
4. 简单单元测试，测试接口是否正常。

# 📌 建议你的练习顺序（直接在你现有项目迭代）

1. 统一接口返回格式 + 完善后端参数校验
2. 给客户管理增加编辑功能
3. 客户列表做分页
4. 做登录功能 + 登录拦截装饰器
5. Flask‑Migrate 学习，管理数据表变更
6. 实现网点、押运人员完整 CRUD（增删改查）

> 
> 每完成一个小功能，就做一次 git commit 阶段性提交，方便回退。




# 你现在要做的事，按顺序一步步来，不要跳，不要急着写新页面

> 
> 当前现状：登录、session 存权限、客户列表接口全部跑通；超级 admin 逻辑已经想好；**还没有真正验证权限拦截是否生效**。

## 第 1 步：把权限装饰器代码复制到 routes.py

复制这个 `require_perm` 装饰器，放到 routes.py 顶部，api_bp 定义之后的位置：

```
from functools import wraps
from flask import session, jsonify

def require_perm(perm_key):
    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            perms = session.get("permissions", [])
            user_id = session.get("user_id")
            if not user_id:
                return jsonify({"code":401,"msg":"未登录"})
            # admin超级用户直接放行
            if "admin" in perms:
                return f(*args, **kwargs)
            if perm_key not in perms:
                return jsonify({"code":403,"msg":"没有操作权限"})
            return f(*args,**kwargs)
        return inner
    return decorator
```

## 第 2 步：给你的接口加上装饰器

示例：

```
@api_bp.route("/api/customer/list", methods=["GET"])
@require_perm("customer:list")
def customer_list_api():
    # 你的原有代码
```

后续新增、编辑、删除接口，分别加上：

- `@require_perm("customer:add")`
- `@require_perm("customer:edit")`
- `@require_perm("customer:delete")`

保存，重启 Flask。

> 
> 现在用你现在 admin 账号登录，因为 permissions 里面有`admin`，所有接口直接放行，照常访问。

## 第 3 步：造一个普通测试用户（**不用写页面，用数据库工具**）

用 DB Browser for SQLite 打开 `crm.db`

1. 新建角色：角色名称：客户只读员
2. 在中间表 `role_permission`：给这个角色只绑定权限 `customer:list`，**不要勾选 admin**
3. 在 `user_role` 中间表，新建一条关联，把一个测试用户和这个角色绑定。

> 
> 这个普通用户登录后 session 权限只会是 `["customer:list"]`。

## 第 4 步：测试权限效果（核心验证）

1. 登录这个普通账号，看控制台 print 输出，确认权限只有 `['customer:list']`
2. ✅访问客户列表接口：可以正常返回数据（200）
3. ✅手动调用新增客户接口（比如浏览器 F12 复制接口地址访问），预期返回 `code:403 没有操作权限`

> 
> 如果出现 403，代表后端鉴权完整生效。

## 第 5 步：处理前端页面按钮权限

打开 `templates/customer.html`
修改按钮判断，兼容 admin 超级用户：

```
{% if "admin" in session.permissions or "customer:add" in session.permissions %}
<button class="layui-btn" id="addBtn">新增客户</button>
{% endif %}

{% if "admin" in session.permissions or "customer:delete" in session.permissions %}
<button class="layui-btn layui-btn-danger">删除</button>
{% endif %}
```

- admin 账号：按钮全部显示
- 普通只读账号：新增、删除按钮直接隐藏

## ✅做完上面，你的整套权限逻辑就全部调试完毕

> 
> ⚠**现在不要写角色管理、用户管理页面！** 那是后面收尾才做的。

# 做完测试之后两种选择

1. 课程作业到此够用：权限逻辑跑通即可，权限维护靠数据库工具手动改数据。
2. 如果要做完整成品：再去写用户管理、角色管理页面和对应的增删改接口。

## 现在你马上动手的最小行动

1. 粘贴装饰器代码
2. 给 customer_list_api 加上`@require_perm("customer:list")`，重启 flask
3. 用数据库工具创建只读角色 + 普通测试账号，登录测试 403 拦截。

> 
> 你测试完告诉我：普通用户调用新增接口是返回 403，还是直接成功？我帮你判断哪里还有问题。

 如何在数据库中添加普通用户权限？

 如何验证权限拦截是否生效？

 如何在代码中使用权限装饰器？