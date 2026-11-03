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










 # 1、先搞懂：RESTful 到底是干啥的？

以前老写法（你大概率之前见过）：

- 新增用户：`/user/add`
- 修改用户：`/user/edit`
- 删除用户：`/user/del`
- 查询用户：`/user/list`

👉 特点：**URL 里面带动词 add /edit/del**，一个动作一条新地址。

REST 的思路反过来：

> 
> URL 只代表【资源】（就是用户、角色这些东西，用名词）
> **动作交给【请求方式 GET/POST/PUT/DELETE】来区分**

同一个地址 `/api/user`，发不同请求，干不同事：

- ✅ GET 到 `/api/user` → 查询列表
- ✅ POST 到 `/api/user` → 新增一个用户
- ✅ GET 到 `/api/user/1` → 查询 id=1 的单个用户
- ✅ PUT 到 `/api/user/1` → 修改 id=1 的用户
- ✅ DELETE 到 `/api/user/1` → 删除 id=1 的用户

> 
> URL 不变，**靠请求方式区分要干什么**，这就是 REST 的核心。

---

# 2、但是！有一个最大难点：HTML 原生表单只认识 GET、POST

你写 `<form action="xxx" method="POST">`
method 只能写 `get` 和 `post`，**写 put、delete 浏览器不认，直接失效**。

所以：
✅ 查询列表、搜索：table 自带 GET，完全没问题，不用折腾
✅ 新增：用 POST，表单 ajax 直接可以发，简单
❌ 修改、删除：我们想要用 PUT / DELETE，**只能用 jQuery ajax 去发**，不能直接表单提交

这就是刚才代码里重点写 `$.ajax({type:"PUT"})` 的原因。

---

# 3、举两组对比，一眼看懂差别

## 老式写法（非 REST，好理解，但不规范）

1. 查询列表：`GET /user/list`
2. 新增：`POST /user/add`
3. 修改：`POST /user/edit`
4. 删除：`GET /user/del?id=1`

## REST 写法（我们现在要学的）

1. 查询列表：`GET /api/user`
2. 新增：`POST /api/user`
3. 查询单条：`GET /api/user/1`
4. 修改：`PUT /api/user/1`
5. 删除：`DELETE /api/user/1`

> 
> 你看：url 干净了，没有 add、edit、del 这些动词。

---

# 4、拿你现在【用户管理】流程串一遍

你的页面流程：

1. 打开页面 → layui table 自动发 GET 请求拿用户列表
→ 接口：`GET /api/user` ✅
2. 点【新增】按钮，弹出表单，填完提交保存
→ ajax 发 POST → `POST /api/user` ✅
3. 点【编辑】，先查这条数据回填到表单
→ ajax 发 GET → `GET /api/user/1` ✅
4. 编辑表单提交保存修改
→ ajax 发 PUT → `PUT /api/user/1` ✅
5. 点删除，弹出确认，确认后删掉这条
→ ajax 发 DELETE → `DELETE /api/user/1` ✅

👉 所有动作，就两个 url 模板：

- `/api/user` （列表、新增）
- `/api/user/:id` （查单条、改、删）

---

# 5、两个容易混淆的点，单独说

### ① PUT 是什么意思？全量更新

PUT 要求：你要把这个用户**完整信息全部传过去**
比如用户有 username、phone、status
你修改的时候，三个字段都要传给后端，后端整体覆盖保存。

> 
> 还有一个 PATCH：局部更新，只传你改的那一个字段，新手先不用碰。

### ② 为什么有时候要伪装成 POST？

有些 Nginx、服务器防火墙，会拦截 PUT、DELETE 请求，直接 403 报错。
兜底方案：请求方式仍然写 POST，额外带一个参数 `_method="PUT"`
后端收到 POST 之后，自己判断这个参数，走修改逻辑。

> 
> 这个是兼容方案，优先直接用原生 PUT/DELETE，出问题再用这个。

---

# 6、和你 Layui 怎么配合？（最关键）

layui table 本身就是 GET，天然适配 REST 查询列表，**表格代码几乎不用改**。
只有：新增弹窗、编辑弹窗、删除按钮这三处，我们手写 ajax，指定 type。

举极简删除例子，只看重点：

```
// 点击删除
layer.confirm('确定删除？', function(){
  $.ajax({
    url: "/api/user/" + row.id,  // 资源地址
    type: "DELETE",              // 动作：删除
    success: function(res){
      layer.msg("删除成功");
      table.reload("userTableId",{},true);
    }
  })
})
```

新增：

```
$.ajax({
  url: "/api/user",
  type: "POST", // 动作：新增
  contentType: "application/json",
  data: JSON.stringify(data.field),
  success: function(res){ ... }
})
```

编辑保存：

```
$.ajax({
  url: "/api/user/" + id,
  type: "PUT", // 动作：修改
  contentType: "application/json",
  data: JSON.stringify(data.field),
  success: function(res){ ... }
})
```

---

# 7、一句话总结

REST 不是什么高大上框架，只是一套约定：
**URL 只写东西（用户、角色），干什么操作，由 GET/POST/PUT/DELETE 这个请求方式来说明。**

你看哪里还懵？
是：
A. 路由看不懂？
B. ajax 发 PUT/DELETE 看不懂？
C. 不知道什么时候该用哪个？
 A 
 A 
 A 
 A 
> ✅ **你完全可以继续用老写法（/user/add、/user/edit、/user/del），没有任何强制要求，你的小后台管理系统完全够用。**
> REST 只是一套**约定规范**，不是程序必须遵守的语法，不是不写就跑不起来。

下面分开讲：什么时候适合老写法、什么时候才值得往 REST 上凑，以及两者的优缺点。

## 一、老式写法（你原来的方式）

路由长这样：

```
GET  /user/list        查询列表
POST /user/add         新增
POST /user/edit        修改
GET  /user/del?id=1    删除
```

优点：

1. **好理解、一眼看懂**，url 自带动词，看到地址就知道是干啥；
2. 不用管 PUT / DELETE，全部 GET、POST，nginx、防火墙、表单全都兼容，不会出现 405、被拦截；
3. 新手写 CRUD，开发速度快，坑少；
4. 不用区分 PUT 全量 / PATCH 局部更新，不用纠结语义。

缺点：

1. 接口没有统一规则，项目大了容易写乱；
比如有人写 `/user/delete`，另一个人写 `/user/remove`，命名五花八门；
2. 接口数量膨胀，一个资源 5 个动作，就要 5 条路由；
3. **前后端分离、对外提供 API 给别的系统调用的时候，可读性差**。
比如别的系统对接你的接口，看 url 才能猜功能，没法靠请求方法统一认知。

## 二、REST 适合什么场景？

REST 最初是为**对外开放 API、多端调用（APP、小程序、第三方系统）**设计的：

```
GET    /api/user        列表
POST   /api/user        新增
GET    /api/user/1      查单条
PUT    /api/user/1      修改
DELETE /api/user/1      删除
```

好处体现在这些场景：

1. **规则统一**：所有资源一套模板。角色、部门、菜单，全是这套玩法，新人接手项目，不用逐个看接口注释；
2. 语义标准，行业共识。面试、进公司团队，很多团队强制这套规范；
3. 缓存天然友好：GET 代表只读，网关可以对 GET 做缓存；POST/PUT/DELETE 代表会改动数据，不缓存；
4. 权限控制好做：资源 + 动作，`user:list`（GET）、`user:add`（POST）、`user:edit`（PUT）、`user:del`（DELETE），和你现在的权限字符串刚好匹配。

但是！**REST 有代价**：

- 要处理 PUT/DELETE 被网关拦截的坑；
- 不能直接原生 form 提交，全部要 ajax；
- 还要区分 PUT（全量）、PATCH（局部），多一层概念；
- 小后台、只有你一个人维护、只有 layui 网页端使用 → 收益很低，麻烦变多。

## 三、给你一个非常务实的选择方案（贴合你现在这个 Flask+Layui 后台）

### 方案 A（省心推荐，你自己独立开发自用）

👉 **继续老写法，不用硬上 REST！**

```
/user/list
/user/add
/user/edit
/user/del
```

好处：少踩坑，开发快，对你的业务完全够用。

> 
> 很多公司内部管理后台，全是这种写法，跑很多年，一点问题没有。

### 方案 B（想学规范、练技术，以后面试 / 进团队用）

👉 改成 REST 风格，当作练习。
**目的不是 “程序必须这么跑”，是熟悉这套行业标准，以后遇到要求 REST 的项目不会懵。**
就像学设计模式，很多小项目不用，但你得知道是什么。

### 方案 C（折中方案，很多人在用）

URL 稍微规范一点，但是只用 GET/POST，避开 PUT、DELETE 的坑：

```
GET    /api/user        列表
POST   /api/user/add    新增
POST   /api/user/update 修改
POST   /api/user/remove 删除
```

兼顾一部分整洁，又不碰 PUT/DELETE 的兼容问题。

## 四、一句话总结

**REST 不是 “正确写法”，只是一种标准化写法。**

- 如果你目标：快速写完这个后台，自己用、简单稳定 → 老写法完全没问题，没必要凑 REST；
- 如果你目标：练手、以后找工作、对接第三方 API、团队协作 → 值得学 REST，熟悉这套约定。

> 
> 补充一句：很多人踩坑就是盲目跟风 REST，小项目硬上，然后被 nginx、网关拦截 PUT/DELETE，白白浪费时间。



数据库的备份脚本
http://127.0.0.1:5000/db/backup
定时任务需要写