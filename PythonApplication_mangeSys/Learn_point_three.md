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


列表接口 `/user/list`，前端传：

- url：`?page=1&limit=10`（分页，args）
- body：开始时间、结束时间、选中的角色（form/json）
这时你必须分开读取，**request 就是干这个的**。
- 1. **底层本质**：Flask 里前端传来的所有数据，全部都存在 `request` 对象里；之前没直接写 `request`，只是框架 / 封装帮你隐藏了它，并不是不需要它。
2. **三大参数来源，对应三种读取方式**
   - `request.args`：url 问号后面的参数，多用于分页、搜索筛选
   - `request.form`：表单提交数据，适配 Layui 传统表单
   - `request.get_json()`：json 格式请求体，适合 axios 前后端分离接口
3. **主动使用 request 的核心价值**
   - 分清参数来源，参数不会混淆
   - 方便设置默认值、类型转换、做参数校验，防止脏数据
   - 可以拿到额外信息：请求方式、客户端 IP、请求头、上传文件
   - 代码清晰，方便调试、维护，适合后台管理接口
4. **适用场景（你的项目）**：Layui 表格分页、时间 / 复选框筛选、新增编辑提交、JSON 接口；简单页面可以靠封装简化，复杂业务接口建议显式使用 `request`。
5. 一句话区分：`request` 是**接收前端发来的数据（入）**；`render_template` / `jsonify` 是**返回数据给前端（出）**。




### layer 的 type 规则（layui‑layer）

- **`type: 0`**：信息框、alert，content 传**字符串文本**（默认）
- **`type: 1`**：页面层，content 传 **HTML 片段 / DOM 片段**（我们用模板`$("#editTpl").html()`拿到 html 字符串 → 用 type=1 ✅正确）
- **`type: 2`**：iframe 层，content 传 **url 地址**，会打开一个内嵌网页 iframe，例如 `content:"/user/form"`




### 一句话总结

- **`layer`：是 layui 的弹窗模块对象（全局工具）**，用来打开弹窗、msg、confirm、关闭弹窗等，是**工具本身**
- **`layero`：是当前这个弹窗的 DOM jQuery 对象**，代表**刚刚弹出来的这个弹窗页面容器**，用来在弹窗内部找元素、操作弹窗 DOM

```
layer.open({
    type:1,
    title:"新增用户",
    success:function(layero, index){
        // 这里：layero、index 是 success 回调自动传入的两个参数
        // layero 👉 弹窗容器的jQuery对象
        // index  👉 弹窗编号，用来 layer.close(index)
    }
})
```

---

## 详细对比

### 1. layer（模块）

```
var layer = layui.layer;
```

✅ 作用：调用弹窗所有功能

```
layer.msg('提示');
layer.confirm('确认？');
layer.close(index);
layer.open({...});
```

👉 它是**工具 API**，整个页面共用这一个。

### 2. layero（弹窗 DOM 容器，success 回调参数）

`layero` 本质就是 `$(弹窗外层div)`，是 jQuery 包装对象
✅ 作用：**在弹窗里面查找元素**

```
success:function(layero, index){
    // 在弹窗内部查找 #username 输入框（推荐写法，防止和父页面id冲突）
    layero.find('[name="username"]').val('test');
}
```

> 
> ⚠️ 坑：如果你直接用 `$('[name="username"]')`，页面复杂的时候，有可能匹配到父页面同名元素；
> `layero.find()` 限定只在当前弹窗里面搜索，更安全。

### 3. index（弹窗编号，顺带讲）

`index` 是弹窗的数字 ID，用来关闭这个弹窗：

```
layer.close(index);
```

---

## 结合你现在新增用户弹窗的例子

```
$('#addUserBtn').click(function(){
    layer.open({
        type:1,
        title:"新增用户",
        area:["520px","420px"],
        content:$("#editTpl").html(),
        success:function(layero, index){
            // layero：当前弹窗容器，只在这个弹窗生效
            // 清空表单
            form.val('editForm', {
                id:"",
                username:"",
                password:"",
                email:"",
                phone:"",
                role_id:"",
                status:1
            });
            // 只在这个弹窗里面查找元素
            // layero.find('input[name="username"]').focus();
        },
        btn: ['立即提交','重置'],
        yes:function(index, layero){
            // yes回调里面也能拿到 layero 和 index
            let data = form.val('editForm');
            $.post("/user/add", data, function(res){
                if(res.code===0){
                    layer.msg("新增成功"); // 这里的 layer 是模块
                    layer.close(index);
                    tableIns.reload();
                }else{
                    layer.msg(res.msg,{icon:2});
                }
            })
            return false;
        }
    })
})
```


# index 弹窗编号

**是的，可以同时打开多个弹窗。**

`layer.open()` 每打开一次弹窗，就会返回一个数字，这个数字就是 `index`。
success、yes 回调函数的第二个参数也会把这个编号传给你。

示例：

```
// open 返回值就是 index
var idx1 = layer.open({title:"弹窗A", type:1, content:"A"});
var idx2 = layer.open({title:"弹窗B", type:1, content:"B"});
```


// 点击"保存"时触发；index 为当前弹层索引，layero 为弹层 DOM 对象
yes: function (index, layero) {

这里为哈是yes ？ 问题是固定写法吗还是自定义？





这里缺少报错

400 w未找到  大多数是缩进问题


2026..11.5


@@@@@@##############代码备份
 file_list = request.files.getlist("files")
    if not file_list or file_list[0].filename == "":
        return jsonify({"code":400, "msg":"file type no select"}), 400

    result_list = []
    uploader_id = request.uid if hasattr(request, "uid") else 0

    try:
        for file in file_list:
            if not file.filename:
                continue
            if not allowed_file(file.filename):
                result_list.append({"filename":file.filename, "status":"fail", "msg":"can't file type"})
                continue

            safe_original_name = secure_filename(file.filename)
            parts = safe_original_name.rsplit(".", 1)
            if len(parts) >= 2:
                ext = parts[1].lower()
            else:
                ext = ""

           
            # 生成唯一保存文件名（uuid + 文件后缀）
            save_name = generate_unique_save_name(ext)
            # 拼接文件在磁盘上的完整绝对保存路径
            save_path = get_full_save_path(save_name)
            print("✅ filepath===============：", save_path)
            # 提取保存路径中的目录部分
            save_dir = os.path.dirname(save_path)
            # 如果目录不存在则自动创建，exist_ok=True 目录已存在时不报错
            os.makedirs(save_dir, exist_ok=True)


            file_content = file.read()
            file_size = len(file_content)
            file_hash = hashlib.sha256(file_content).hexdigest()

            exist_record = db.session.query(FileRecord).filter_by(file_hash=file_hash, is_deleted=False).first()
            if exist_record:
                result_list.append({
                    "original_name": safe_original_name,
                    "save_name": exist_record.save_name,
                    "file_url": exist_record.file_url,
                    "file_size": exist_record.file_size,
                    "file_hash": file_hash,
                    "status":"success",
                    "msg":"up success ,file  alealy"
                })
                continue

            # 写磁盘
            with open(save_path, "wb") as f:
                f.write(file_content)

            file_url = get_file_access_url(save_name)
            new_record = FileRecord(
                original_name = safe_original_name,
                save_name = save_name,
                file_url = file_url,
                file_size = file_size,
                ext = ext,
                file_hash = file_hash,
                uploader_id = uploader_id
            )
            db.session.add(new_record)   # ✅只add，循环内不commit

            result_list.append({
                "original_name": safe_original_name,
                "save_name": save_name,
                "file_url": file_url,
                "file_size": file_size,
                "file_hash": file_hash,
                "status":"success"
            })

        # =========循环全部结束，外面统一commit一次=========
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        raise e

    return jsonify({"code":200, "msg":"file many success", "data":result_list})






    2026.11.6
    #####   
    hashlib.sha256() 的使用

    hashlib.sha256() 是 Python 标准库 hashlib 中用于生成 SHA-256 哈希值（摘要）的方法。它常用于‌文件完整性校验‌、‌数据指纹生成‌以及‌密码存储‌（需配合加盐）。

SHA-256 是一种单向加密哈希算法，具有‌不可逆性‌（无法从哈希值还原原文）和‌唯一性‌（不同输入极大概率产生不同输出）。

import hashlib

# 1. 准备数据
data = "Hello, World!"

# 2. 创建 SHA-256 哈希对象
# 方法一：直接传入字节数据
sha256_hash = hashlib.sha256(data.encode('utf-8'))

# 方法二：先创建空对象，再 update 数据（适合分块处理或多次追加数据）
# sha256_hash = hashlib.sha256()
# sha256_hash.update(data.encode('utf-8'))

# 3. 获取哈希值
# hexdigest() 返回十六进制字符串（常用，易读）
hex_digest = sha256_hash.hexdigest()
print(f"SHA-256 哈希值: {hex_digest}")
# 输出: a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e

# digest() 返回原始字节形式
byte_digest = sha256_hash.digest()



2026.11.9


# 动创建数据库会话代码片段

```
# 从app配置拿到数据库连接地址
db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
# 1. 创建数据库引擎
engine = create_engine(db_uri)
# 2. 制造会话工厂类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 3. 实例化得到一个数据库会话对象
db_session = SessionLocal()
```

> 
> 平时 Flask‑SQLAlchemy 我们都是直接用全局对象 `db.session`；
> **这段代码是绕开 Flask‑SQLAlchemy 的全局 db，原生使用 SQLAlchemy 底层 API 手动造会话。**

## 逐个拆解每一行

### 1. `db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]`

- `SQLALCHEMY_DATABASE_URI` 就是你配置文件里面写的数据库连接串，例如：
`mysql+pymysql://root:123456@127.0.0.1:3306/testdb`
- `current_app.config` 读取当前 flask 应用的配置，拿到数据库地址。

### 2. `engine = create_engine(db_uri)`

`engine` 数据库引擎，SQLAlchemy 的核心。

- 作用：管理数据库连接池，负责和 mysql 建立连接、执行 SQL。
- Flask‑SQLAlchemy 内部，它底层也会自动帮你创建 engine，只是你看不见。
- 现在我们手动写，直接根据连接字符串自己构建引擎。

### 3. `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`

`sessionmaker()`：**会话工厂函数**，生成一个类，不是直接生成会话实例。

参数解释：

1. `bind=engine`：绑定刚刚创建好的数据库引擎，后续会话都走这个 engine 去连数据库。
2. `autocommit=False`：关闭自动提交。必须手动调用 `.commit()` 才把改动真正写入数据库。出错可以`.rollback()`回滚。（生产环境几乎都是 False）
3. `autoflush=False`：关闭自动刷新。
   - True：查询前自动把 session 内对象变化刷新到数据库；
   - False：需要你手动控制什么时候同步，适合批量处理、上传这种批量业务，减少隐式 SQL，性能更好。

> 
> `SessionLocal` 是一个**类**，不是真正会话对象，名字约定俗成叫 SessionLocal。

### 4. `db_session = SessionLocal()`

调用工厂类，实例化，得到真正可以干活的会话对象。
之后：

- `db_session.add()` 添加模型
- `db_session.execute()` 执行 sql
- `db_session.commit()` 提交事务
- `db_session.rollback()` 回滚
- `db_session.close()` 关闭连接

---

# 和平时写的 `db.session` 对比

## 方式 A：你平常写（Flask‑SQLAlchemy 封装好）

```
from exts import db

@bp.route("/xxx")
def test():
    db.session.add(model_obj)
    db.session.commit()
```

- 由 Flask‑SQLAlchemy 接管：自动创建 engine、自动创建 session、请求结束**自动关闭会话**。
- 请求生命周期结束，框架帮你回收连接。

## 方式 B：本上传接口用的【原生手动会话】

```
engine = create_engine(db_uri)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = SessionLocal()

try:
    # 业务操作 db_session.add() ...
    db_session.commit()
except Exception as e:
    db_session.rollback()
finally:
    db_session.close() # ⚠️必须自己手动关闭！！
```

### 为什么这个上传接口要这么写？

注释写了：**接口内部直接构造会话，不依赖 exts 全局变量**。
场景原因：

1. 有些特殊场景：蓝图 / 模块不想依赖外部`exts.py`全局 db 对象，降低模块耦合，模块可以独立拿出来运行。
2. 批量处理文件上传，想要精细控制事务：全部文件成功才 commit，任意一个异常全部 rollback。
3. 自己完全掌控会话生命周期，什么时候开启、回滚、关闭，全部自己写。

> 
> ⚠️巨大风险点（代码里 finally 写了 close，很关键）
> 手动创建会话**框架不会帮你自动关闭连接**！如果忘记写 `db_session.close()`，数据库连接不会释放，连接池会被耗尽，服务卡死。
> 所以代码放在 `try‑except‑finally`，无论成功失败，`finally` 一定执行 close。

## 两个关键概念区分（面试）

1. **Engine（引擎）**：管数据库连接池，和数据库建立通信通道。
2. **Session（会话）**：工作单元，存放 ORM 对象，管理事务（commit /rollback）。

> 
> engine 是水管；session 是一次干活的工作会话。

## 缺点，这个写法的弊端

1. 重复创建 engine：**每来一次请求就 create_engine 一次是不推荐的！**

> 
> 这个代码在这里有瑕疵！engine 应该全局只创建一次，不应该在接口函数内部每次请求新建 engine。
> engine 创建代价高，频繁新建会损耗性能。
> 正确做法：engine 放到模块顶层，接口内只创建 SessionLocal 会话，不要每次请求 create_engine。

2. 需要手动处理 close、rollback、commit，全部自己管，很容易漏写，造成连接泄漏。

## 总结记忆

1. `create_engine`：造数据库引擎（连接池）
2. `sessionmaker`：造会话工厂类
3. `SessionLocal()`：实例出 db_session 会话对象
4. 手动会话：不受 Flask‑SQLAlchemy 全局 db 管控，自己管事务和关闭
5. 一定要 `finally{ db_session.close() }`，否则连接泄露。
6. 不要在接口里面每次请求重复 create_engine，这是这段代码的瑕疵。



####2026.11.10 计算hash的值传递图片的时候

Get-FileHash C:\Users\廉超\Desktop\桌面图标\30adcbef76094b369274c021be0f50cb8f109d69.webp -Algorithm SHA256


@upload_bp.route("/chunk", methods=["POST"])
def chunk_upload():
    # ---------- 1、读取并校验参数 ----------
    # 获取分片上传标识ID，前端生成，用于区分同一次上传的所有分片
    upload_id = request.form.get("upload_id", "").strip()
    # 获取当前分片的序号
    part_num_str = request.form.get("part_num", "").strip()
    # 获取本次上传总的分片数量
    total_parts_str = request.form.get("total_parts", "").strip()
    # 获取前端计算好的文件sha256哈希值，用于秒传和上传后完整性校验
    file_hash = request.form.get("file_hash", "").strip().lower()
    # 获取原始上传文件名（用户本地的文件名）
    original_name = request.form.get("original_name", "").strip()
    # 获取上传过来的分片二进制文件对象
    chunk_file = request.files.get("chunk")

    # 校验全部必填参数，任意一个为空直接返回参数错误
    if not all([upload_id, part_num_str, total_parts_str, file_hash, original_name, chunk_file]):
        return jsonify({"code": 400, "msg": "参数不完整"}), 400

    # 防路径穿越攻击：正则校验upload_id格式，避免特殊字符导致目录漏洞
    if not UPLOAD_ID_PATTERN.match(upload_id):
        return jsonify({"code": 400, "msg": "非法的 upload_id"}), 400

    # 将分片序号、总分片数字符串转为int类型，转换失败说明传参格式不对
    try:
        part_num = int(part_num_str)
        total_parts = int(total_parts_str)
    except ValueError:
        return jsonify({"code": 400, "msg": "分片编号必须是数字"}), 400

    # 校验分片编号合法性：分片序号不能小于1，总分片不能小于1，当前分片不能超过总分片数
    if part_num < 1 or total_parts < 1 or part_num > total_parts:
     return jsonify({"code": 400, "msg": "分片编号越界"}), 400

    # 解析原始文件名，提取文件后缀名
    name_parts = original_name.rsplit(".", 1)
    ext = name_parts[1].lower() if len(name_parts) > 1 else ""
    # 如果配置了文件后缀白名单，判断当前后缀是否允许上传，不允许直接拒绝
    if ALLOWED_EXTS and ext not in ALLOWED_EXTS:
        return jsonify({"code": 400, "msg": f"不允许的文件类型: .{ext}"}), 400

    # ---------- 2、【秒传前置】第一片就查 hash，命中直接返回 ----------
    # 前端应该在上传前先调一个 /check 接口；这里在 part_num==0 时兜底再查一次
    # 根据文件hash查询数据库，判断该文件是否已经上传完成且未被删除，实现秒传功能
    exist_record = FileRecord.query.filter_by(
        file_hash=file_hash, is_deleted=False
    ).first()
    if exist_record:
        # 秒传命中：清理可能已经上传的临时分片
        _cleanup_chunks(upload_id)
        return jsonify({
            "code": 200,
            "msg": "秒传成功",
            "data": exist_record.to_dict(),
            "instant": True
        })

    # ---------- 3、流式保存分片（不读入内存） ----------
    # 获取分片临时存储目录配置
    temp_dir = Config.CHUNK_TEMP_FOLDER
    # 如果临时目录不存在，自动创建目录，exist_ok=True代表目录已存在不会抛异常
    os.makedirs(temp_dir, exist_ok=True)
    # 拼接分片的完整存储路径
    chunk_path = os.path.join(temp_dir, f"{upload_id}_part_{part_num}")
    # 先写入.tmp临时后缀文件，分片完全写完之后再重命名为正式分片文件，防止程序中断产生半完成的无效分片
    chunk_path_tmp = chunk_path + ".tmp"
    # 记录当前分片已经写入的字节大小，用于判断单分片大小超限
    written = 0
    try:
        # 二进制模式打开临时文件，准备写入分片数据
        with open(chunk_path_tmp, "wb") as out_f:
            # 循环读取请求流中的分片数据，按BUF_SIZE缓冲区大小读取，避免大分片全部加载进内存
            while True:
                buf = chunk_file.stream.read(BUF_SIZE)
                if not buf:
                    break
                written += len(buf)
                # 判断单个分片大小是否超过配置的最大分片限制
                if written > MAX_CHUNK_SIZE:
                    # 超出分片限制，删掉临时文件
                    out_f.close()
                    os.unlink(chunk_path_tmp)
                    return jsonify({"code": 400, "msg": f"单个分片超过 {MAX_CHUNK_SIZE // 1024 // 1024}MB"}), 400
                out_f.write(buf)
        # 原子rename，避免半写文件被扫到；把tmp临时文件重命名为正式分片文件，操作系统层面原子操作不会产生中间状态
        os.replace(chunk_path_tmp, chunk_path)
    except Exception as e:
        # 捕获写入分片时的异常，如果临时文件存在就删除，避免残留损坏临时文件
        if os.path.exists(chunk_path_tmp):
            os.unlink(chunk_path_tmp)
        # 将异常堆栈记录到应用日志
        current_app.logger.exception("分片写入失败")
        return jsonify({"code": 500, "msg": f"分片保存失败: {e}"}), 500

    # ---------- 4、扫描已完成分片（排除 .tmp 半写文件） ----------
    # 读取临时目录下面全部文件
    uploaded = os.listdir(temp_dir)
    # 筛选出属于本次upload_id的已经完成的分片，过滤掉tmp临时文件，并且按分片数字从小到大排序
    current_uploaded = sorted(
        [p for p in uploaded if p.startswith(f"{upload_id}_part_") and not p.endswith(".tmp")],
        key=lambda x: int(x.split("_part_")[-1])
    )
    # 已经上传完成的分片数量不等于总分片数，代表文件还没有全部上传完毕，直接返回结果，等待下一个分片请求
    if len(current_uploaded) != total_parts:
        return jsonify({
            "code": 200,
            "msg": f"分片 {part_num} 上传成功",
            "uploaded_count": len(current_uploaded),
            "total_count": total_parts,
            "instant": False
        })

    # ---------- 5、【加锁合并】防并发重复合并 ----------
    # 用一个锁文件：谁先创建谁负责合并；多个分片同时到达全部完成状态，防止多个请求同时执行文件合并逻辑
    lock_path = os.path.join(temp_dir, f"{upload_id}.merge.lock")
    try:
        # O_CREAT 创建文件，O_EXCL 如果文件已存在直接抛FileExistsError，实现互斥锁；写入当前进程pid到锁文件
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
    except FileExistsError:
        # 已经有别的请求在合并了，等它结束就行；返回正在合并标识给前端
        return jsonify({
            "code": 200,
            "msg": "正在合并中",
            "uploaded_count": total_parts,
            "total_count": total_parts,
            "merging": True
        })

    # ---------- 6、流式合并 + 流式算 hash ----------
    try:
        # 根据后缀生成服务器端唯一保存文件名
        save_name = generate_unique_save_name(ext)
        # 获取文件在磁盘上完整存储路径
        final_save_path = get_full_save_path(save_name)
        # 获取文件存放目录，如果目录不存在就创建
        out_dir = os.path.dirname(final_save_path)
        os.makedirs(out_dir, exist_ok=True)
        # 初始化sha256哈希对象，一边合并分片一边计算完整文件哈希
        sha256 = hashlib.sha256()
        # 统计合并之后完整文件总字节大小
        total_size = 0
        # 二进制模式打开最终输出文件，循环读取每一个分片，流式写入最终文件，不把整个大文件加载内存
        with open(final_save_path, "wb") as out_f:
            for fname in current_uploaded:
                part_path = os.path.join(temp_dir, fname)
                with open(part_path, "rb") as in_f:
                    while True:
                        buf = in_f.read(BUF_SIZE)
                        if not buf:
                            break
                        total_size += len(buf)
                        # 判断合并后的总文件大小是否超过系统配置上限
                        if total_size > MAX_TOTAL_SIZE:
                            raise ValueError(f"总文件超过 {MAX_TOTAL_SIZE // 1024 // 1024 // 1024}GB 限制")
                        sha256.update(buf)
                        out_f.write(buf)
        # 获取后端实际计算出来的文件sha256十六进制字符串
        calc_hash = sha256.hexdigest()

        # ---------- 7、hash 校验 ----------
        # 后端算出来的hash和前端上传携带的hash对比，校验文件上传是否完整无损坏
        if calc_hash != file_hash:
            print(f"⚠️ hash不一致（仅测试提示）：前端={file_hash} 后端={calc_hash}")
            # 删成品 + 清分片 + 删锁
           # if os.path.exists(final_save_path):
          #      os.unlink(final_save_path)
         #   _cleanup_chunks(upload_id)
          #  return jsonify({"code": 500, "msg": "文件校验失败，请重新上传"}), 500

        # ---------- 8、写数据库 ----------
        # 组装数据库FileRecord模型对象，保存文件元信息到数据库
        new_record = FileRecord(
            original_name=_sanitize_chinese_filename(original_name),  # 保留中文
            save_name=save_name,
            file_url=get_file_access_url(save_name),
            file_size=total_size,
            ext=ext,
            file_hash=file_hash,
            uploader_id=getattr(request, "uid", 0)
        )
        db.session.add(new_record)
        db.session.commit()
        # 合并成功：清理分片 + 删锁；上传完成删除所有临时分片文件
        _cleanup_chunks(upload_id)
        return jsonify({
            "code": 200,
            "msg": "文件上传完成",
            "data": new_record.to_dict()
        })
    except Exception as e:
        import traceback
        traceback.print_exc()   # ← 加这一行，强制把完整堆栈打到终端
        # 数据库操作异常，执行事务回滚
        db.session.rollback()
        current_app.logger.exception("合并失败")
        # 失败时不清分片，保留现场，下次同 upload_id 可以续传
        if os.path.exists(final_save_path):
            os.unlink(final_save_path)
        return jsonify({"code": 500, "msg": f"合并失败: {e}"}), 500
    finally:
        # 锁文件无论如何都要释放；不管合并成功还是失败，必须删除锁文件，否则后续上传会永远卡在merging状态
        if os.path.exists(lock_path):
            try:
                os.unlink(lock_path)
            except OSError:
                pass


def _cleanup_chunks(upload_id: str):
    """清理某个 upload_id 的所有临时分片"""
    temp_dir = Config.CHUNK_TEMP_FOLDER
    # 如果临时目录不存在直接返回，无需清理
    if not os.path.isdir(temp_dir):
        return
    # 遍历临时目录，删除属于本次upload_id全部分片临时文件
    for fname in os.listdir(temp_dir):
        if fname.startswith(f"{upload_id}_part_"):
            try:
                os.unlink(os.path.join(temp_dir, fname))
            except OSError:
                pass


                #########################