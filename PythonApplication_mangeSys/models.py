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
     display_level = self.level
     return {
        "id": self.id,
        "name": self.name,
        "phone": self.phone,
        "email": self.email,
        "address": self.address,
        "level": display_level,
        "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
    }
 # ========== 【新增：用户表，直接追加在后面，前面代码不用改！】 ==========
class User(db.Model):
    __tablename__= "sys_user" # 魔方方法创建对象
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    real_name = db.Column(db.String(50))
    password = db.Column(db.String(100))
    create_time = db.Column(db.DateTime, default=datetime.now)


    #==========={新增权限功能}
    # ========== 【中间表：角色 ↔ 权限，纯中间表，没有额外字段】==========

# =========权限表=========
class Permission(db.Model):
    __tablename__ = "permission"
    id = db.Column(db.Integer, primary_key=True)
    perm_key = db.Column(db.String(64), unique=True, nullable=False) #权限标识，如 customer:delete
    perm_name = db.Column(db.String(64), nullable=False) #中文名称：删除客户

# =========角色表=========
class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(32), unique=True, nullable=False)
    remark = db.Column(db.String(128))
    #角色 <--->权限 多对多
    permissions = db.relationship("Permission", secondary="role_permission", backref="roles")

#角色权限中间表
role_permission = db.Table("role_permission",
    db.Column("role_id",db.Integer,db.ForeignKey("role.id"),primary_key=True),
    db.Column("perm_id",db.Integer,db.ForeignKey("permission.id"),primary_key=True)
)

#用户角色中间表
user_role = db.Table("user_role",
    db.Column("user_id",db.Integer,db.ForeignKey("user.id"),primary_key=True),
    db.Column("role_id",db.Integer,db.ForeignKey("role.id"),primary_key=True)
)

#用户表
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32),unique=True,nullable=False)
    password = db.Column(db.String(128),nullable=False)
    #用户 <--->角色 多对多
    roles = db.relationship("Role", secondary=user_role, backref="users")

    # 获取该用户全部权限key集合（去重）
    def get_perms(self):
        perm_set = set()
        for role in self.roles:
            for p in role.permissions:
                perm_set.add(p.perm_key)
        return perm_set









    # 网点
class Org(db.Model):
    __tablename__ = "org"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment="网点名称")
    address = db.Column(db.String(200), comment="地址")
    create_time = db.Column(db.DateTime, default=datetime.now)

# 押运人员
class Escort(db.Model):
    __tablename__ = "escort"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, comment="姓名")
    phone = db.Column(db.String(20), comment="手机号")
    id_card = db.Column(db.String(30), comment="身份证号")

    org_id = db.Column(db.Integer, db.ForeignKey("org.id"), comment="所属网点id")
    # 关系映射
    org = db.relationship("Org", backref="escorts")

    create_time = db.Column(db.DateTime, default=datetime.now)

      
