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
      
