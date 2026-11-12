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
    hire_date = db.Column(db.Date, nullable=True)  # ✅ 新增，日期类型，允许为空

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
#class Org(db.Model):
 #   __tablename__ = "org"
  #  id = db.Column(db.Integer, primary_key=True)
  #  name = db.Column(db.String(100), nullable=False, comment="网点名称")
  #  address = db.Column(db.String(200), comment="地址")
  #  create_time = db.Column(db.DateTime, default=datetime.now)

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

    #### 文件上传
from datetime import datetime, timezone
from sqlalchemy import func

class FileRecord(db.Model):
    __tablename__ = 'file_record'

    id = db.Column(db.Integer, primary_key=True, comment='主键')
    original_name = db.Column(db.String(255), nullable=False, comment='原始文件名')
    save_name = db.Column(db.String(255), nullable=False, unique=True,
                          comment='存储文件名(UUID)')
    file_url = db.Column(db.String(500), nullable=False, comment='访问地址')
    file_size = db.Column(db.BigInteger, nullable=False, default=0,
                          comment='文件大小(字节)')
    ext = db.Column(db.String(20), index=True, comment='扩展名(小写,不带点)')
    content_type = db.Column(db.String(100), comment='MIME类型')
    file_hash = db.Column(db.String(64), index=True, comment='MD5/SHA256,用于秒传去重')

    uploader_id = db.Column(db.Integer, index=True, comment='上传人ID')
    biz_type = db.Column(db.String(50), index=True, comment='业务类型')
    biz_id = db.Column(db.Integer, comment='业务主键')
    is_deleted = db.Column(db.Boolean, nullable=False, default=False, comment='软删除')

    create_time = db.Column(
        db.DateTime, nullable=False, index=True,
        default=lambda: datetime.now(timezone.utc),  # ORM 层默认值, 统一 UTC
        server_default=func.now()                     # 绕过 ORM 时也有默认值
    )
    update_time = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f'<FileRecord id={self.id} name={self.original_name!r}>'

    def to_dict(self):
     return {
        "id": self.id,
        "original_name": self.original_name,
        "save_name": self.save_name,
        "file_url": self.file_url,
        "file_size": self.file_size,
        "ext": self.ext,
        "file_hash": self.file_hash,
        "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S")
    }
 #  写网点管理相关的代码
 # 1. 网点管理（只存网点基础信息）
# 1. 网点管理（只存网点基础信息）
class Org(db.Model):
    __tablename__ = "org"
    id = db.Column(db.Integer, primary_key=True, comment="网点ID")
    branch_code = db.Column(db.String(64), nullable=False, unique=True, comment="网点编号")
    name = db.Column(db.String(128), nullable=False, comment="网点名称")
    branch_type = db.Column(db.SmallInteger, nullable=False, comment="网点类型：1银行网点，2自助点，3金库")
    region = db.Column(db.String(128), default="", comment="所属区域")
    address = db.Column(db.String(256), default="", comment="地址")
    longitude = db.Column(db.Numeric(10,6), nullable=True, comment="经度")
    latitude = db.Column(db.Numeric(10,6), nullable=True, comment="纬度")
    status = db.Column(db.SmallInteger, default=1, comment="状态：1启用 0停用")
    remark = db.Column(db.String(512), default="", comment="备注")
    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")

    # 关系只是用来查询，页面不再内嵌维护
    #staffs = db.relationship("OrgStaff", back_populates="org", lazy="select")
   # escorts = db.relationship("Escort", back_populates="org", lazy="select")

# 2. 网点人员管理（行长、组长、安保，独立页面CRUD，带头像）
#class OrgStaff(db.Model):
 #   __tablename__ = "org_staff"
 #   id = db.Column(db.Integer, primary_key=True, comment="人员ID")
 #   org_id = db.Column(db.Integer, db.ForeignKey("org.id"), nullable=False, comment="所属网点id")
 #   staff_name = db.Column(db.String(64), nullable=False, comment="姓名")
#   staff_role = db.Column(db.SmallInteger, nullable=False, comment="角色：1行长，2组长，3安保")
 # #  staff_phone = db.Column(db.String(20), default="", comment="手机号")
 #   avatar_url = db.Column(db.String(256), default="", comment="人员照片地址")
#    create_time = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    # ✅ 这里用 back_populates，名字和Org里的relationship名字对应！
  #  org = db.relationship("Org", back_populates="staffs", lazy="select")
# 3. 押运员管理（独立页面CRUD）
#class Escort(db.Model):
 #   __tablename__ = "escort"
 #   id = db.Column(db.Integer, primary_key=True)
  #  name = db.Column(db.String(50), nullable=False, comment="姓名")
  #  phone = db.Column(db.String(20), comment="手机号")
  #  id_card = db.Column(db.String(30), comment="身份证号")
  #  org_id = db.Column(db.Integer, db.ForeignKey("org.id"), comment="所属网点id")
  #  create_time = db.Column(db.DateTime, default=datetime.now)
 # org = db.relationship("Org", back_populates="escorts", lazy="select")

 # 新网点表，完整字段，全新表
class OrgNew(db.Model):
    __tablename__ = "org_new"
    id = db.Column(db.Integer, primary_key=True, comment="主键")
    branch_code = db.Column(db.String(64), nullable=False, unique=True, comment="网点编号，不可重复")
    name = db.Column(db.String(128), nullable=False, comment="网点名称")
    branch_type = db.Column(db.SmallInteger, nullable=False, comment="网点类型：1银行网点，2自助点，3金库")
    region = db.Column(db.String(128), default="", comment="所属区域")
    address = db.Column(db.String(256), default="", comment="详细地址")
    longitude = db.Column(db.Numeric(10,6), nullable=True, comment="经度")
    latitude = db.Column(db.Numeric(10,6), nullable=True, comment="纬度")
    status = db.Column(db.SmallInteger, default=1, comment="状态：1启用，0停用")
    remark = db.Column(db.String(512), default="", comment="备注信息")
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False,comment="记录创建时间")


      
