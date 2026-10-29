
                    2026.10.29
### 先说结论

这些 `PRAGMA main.table_info(xxx)` 是 **SQLite 专属指令**，是 `db.create_all()` 执行的时候自动跑出来的，**不是你登录接口的查询 SQL**！
你现在 `ECHO 已经成功打开了`，只是现在打印的是【启动阶段建表检查的日志】

---

## 1、作用 & 干啥的

`PRAGMA main.table_info("customer")`
翻译：**去查一下 sqlite 数据库里，有没有叫 customer 这张表，以及这张表的字段结构**

流程：

1. 你代码里写了 `db.create_all()`
2. SQLAlchemy 不会直接粗暴删表重建
3. 它先发一堆 `PRAGMA table_info`，挨个查询：`customer、user、role、permission...` 这些表在库里存不存在
4. 如果表不存在 → 执行 `CREATE TABLE` 创建
5. 如果表已经存在 → 啥也不干，跳过
6. 全部检查完，最后 `COMMIT` 提交

> 
> 一句话：**启动时用来核对数据库表，防止重复建表**
> 只在程序刚启动、执行 `db.create_all()` 的一瞬间打印这一堆，登录、查列表的时候，才会出现 `SELECT ...` 这种查询语句。

## 2、能不能改动？

✅ **可以改、可以不让它打印这一堆**，但是一般不建议动。

### 方案 A：不让它执行（推荐，开发常用）

把 `db.create_all()` 注释掉，就不会出来这一堆 PRAGMA 日志了

> 
> 注意：注释之后，**新增的模型、新表不会自动创建**，适合表结构稳定之后使用；新增表的时候再放开跑一次。

### 方案 B：保留 create_all，但是过滤日志（不推荐新手）

单独屏蔽 sqlalchemy 的引擎日志，新手容易把真正想看的登录 SQL 也一起屏蔽掉，得不偿失。

### ❗重要区分（你最关心的验证 N+1）

- `PRAGMA table_info`：启动检查表（现在看到的这批）
- `SELECT * FROM user WHERE username=?`：登录查询用户的 SQL（**这个才是你要找的，用来验证 selectinload**）
- `SELECT ... FROM role WHERE id IN (...)`：预加载角色的 SQL
- `SELECT ... FROM permission WHERE id IN (...)`：预加载权限的 SQL

👉 操作：
现在这些是启动日志，**你现在退出登录，再重新登录一次**，控制台在 POST /api/auth/login 下面，就会出现 SELECT 语句，那就是你要验证的 SQL！

## 3、顺带解释日志末尾的 COMMIT

```
INFO:sqlalchemy.engine.Engine:COMMIT
```

意思：这一轮所有表检查操作结束，提交事务。
因为只是查询表信息，没有新增表，这个 commit 相当于空提交，不修改数据。

## 简单总结

1. 是什么：SQLite 的查询表结构指令，`db.create_all()` 自动调用
2. 干什么：挨个核对数据库里有没有对应的表，存在就跳过，不存在就新建
3. 能不能改：可以注释 `db.create_all()` 来关掉它；表还在频繁新增的时候，建议保留

你现在 ECHO 已经生效了！接下来：清 session、重新登录，盯着控制台找 `SELECT` 开头的 SQL，就能验证 N+1 优化效果。

要不要我教你怎么区分：优化成功（3 条 SELECT）和没优化（多条零散 SELECT）的日志样子？

今天 09:31
