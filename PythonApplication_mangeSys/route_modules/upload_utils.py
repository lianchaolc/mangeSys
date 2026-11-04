
import os
import uuid
import hashlib
from werkzeug.utils import secure_filename
# 导入全局配置
from config import Config
def allowed_file(filename: str) -> bool:
   ## """校验文件扩展名是否在白名单内"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def get_file_sha256(file_stream, chunk_size=4096) -> str:
   ## """流式计算文件SHA256哈希，大文件不会占用大量内存，用于秒传去重、完整性校验"""
    sha256 = hashlib.sha256()
    while chunk := file_stream.read(chunk_size):
        sha256.update(chunk)
    # 重置文件指针，后续可以继续读取文件内容
    file_stream.seek(0)
    return sha256.hexdigest()

#def generate_unique_save_name(ext: str) -> str:
 ##   """生成UUID格式的唯一存储文件名，避免用户上传重名文件导致覆盖"""
  #  return f"{uuid.uuid4().hex}.{ext.lower()}"
def generate_unique_save_name(ext):
    import uuid
    uid = str(uuid.uuid4()).replace("-","")
    if ext:
        return f"{uid}.{ext}"
    else:
        return uid   # 无后缀，不加小数点

def get_full_save_path(save_name: str) -> str:
  ##  """拼接得到文件在服务器上的绝对存储路径"""
    return os.path.join(Config.UPLOAD_FOLDER, save_name)

def get_file_access_url(save_name: str) -> str:
 ##   """生成文件对外可访问的相对URL"""
    return f"/static/upload/{save_name}"