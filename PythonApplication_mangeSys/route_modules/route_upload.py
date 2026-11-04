from concurrent.futures import ThreadPoolExecutor
from werkzeug.formparser import MultiPartParser
from werkzeug.datastructures import Headers
from flask import Blueprint, request, jsonify
# 导入项目公共模块
from config import Config
from route_modules.upload_utils import *
# 导入ORM数据库对象和FileRecord模型（根据你项目实际导入路径调整）
from exts import db
from models import FileRecord


# 初始化上传路由蓝图，和其他业务路由保持一致的注册方式
upload_bp = Blueprint("upload", __name__, url_prefix="/api/upload")
# 初始化IO线程池，异步处理文件写入，不阻塞Flask主线程
thread_pool = ThreadPoolExecutor(max_workers=8)

#####2026.11.5

from models import FileRecord
import os, hashlib
from flask import current_app
from route_modules.upload_utils import allowed_file, secure_filename, generate_unique_save_name, get_full_save_path, get_file_access_url
from flask import Blueprint, request, jsonify, current_app
from models import FileRecord
import os
import hashlib
from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker
from route_modules.upload_utils import allowed_file, secure_filename, generate_unique_save_name, get_full_save_path, get_file_access_url

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')
# 【兜底】app上下文销毁时自动清理session，解决绑定残留
@upload_bp.teardown_request
def shutdown_session(exception=None):
    db.session.remove()

# -------------------------- 接口：多文件上传（优化版，规避session绑定bug） --------------------------
# -------------------------- 接口：多文件上传（修复版） --------------------------
# -------------------------- 多文件上传最终版 --------------------------

   ##### 文件多种格式
        # 支持的后缀，全部小写，多后缀写完整如 tar.gz
ALLOW_EXTS = {
    "png", "jpg", "jpeg", "gif", "bmp","webp",
    "pdf", "doc", "docx", "xls", "xlsx",
    "zip", "rar", "7z", "tar", "tar.gz", "tar.bz2"
}
def get_file_ext(filename: str):
   # """
   # 提取文件扩展名，支持复合后缀 tar.gz / tar.bz2
   # 返回小写扩展名；无后缀返回空字符串
   # """
    fn = filename.lower()
    # 优先匹配长的复合后缀
    for ext in sorted(ALLOW_EXTS, key=len, reverse=True):
        if fn.endswith(f".{ext}"):
            return ext
    # 没有匹配复合后缀，取最后一个点后面部分
    if "." in fn:
        return fn.rsplit(".", 1)[1]
    return ""


@upload_bp.route("/multi", methods=["POST"])
def multi_file_upload():
    resp_data = {"code": 200, "msg": "多文件上传完成", "data": []}
    resp_code = 200

    # ----------------关键：接口内部直接构造会话，不依赖exts全局变量----------------
    db_uri = current_app.config["SQLALCHEMY_DATABASE_URI"]
    engine = create_engine(db_uri)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = SessionLocal()
    # -------------------------------------------------------------------------

    file_list = request.files.getlist("files")
    result_list = []
    uploader_id = getattr(request, "uid", 0)

    try:
        if not file_list or file_list[0].filename == "":
            resp_data = {"code": 400, "msg": "未选择文件", "data": result_list}
            resp_code = 400
        else:
            file_meta_list = []
            for file in file_list:
                if not file.filename:
                    continue
                if not allowed_file(file.filename):
                    result_list.append({
                        "filename": file.filename,
                        "status": "fail",
                        "msg": "不支持该文件类型"
                    })
                    continue

                safe_name = secure_filename(file.filename)
                safe_name = secure_filename(file.filename)
# 获取扩展名（兼容tar.gz）
                ext = get_file_ext(file.filename)

                base_name = generate_unique_save_name(ext)
                if ext:
                  save_name = f"{base_name}.{ext}"
                else:
                    save_name = base_name

                save_path = get_full_save_path(save_name)

                save_name = generate_unique_save_name(ext)
                save_path = get_full_save_path(save_name)
                print("✅ filepath===============：", save_path)

                content = file.read()
                fsize = len(content)
                fhash = hashlib.sha256(content).hexdigest()

                file_meta_list.append({
                    "original_name": safe_name,
                    "save_name": save_name,
                    "save_path": save_path,
                    "file_url": get_file_access_url(save_name),
                    "file_size": fsize,
                    "ext": ext,
                    "file_hash": fhash,
                    "raw_content": content
                })

            if not file_meta_list:
                resp_data = {"code": 200, "msg": "无有效文件", "data": result_list}
                resp_code = 200
            else:
                hash_list = [item["file_hash"] for item in file_meta_list]
                stmt = select(FileRecord).where(FileRecord.file_hash.in_(hash_list), FileRecord.is_deleted == False)
                exist_rows = db_session.execute(stmt).scalars().all()
                exist_hash_set = {row.file_hash for row in exist_rows}

                for meta in file_meta_list:
                    if meta["file_hash"] in exist_hash_set:
                        result_list.append({
                            "original_name": meta["original_name"],
                            "save_name": meta["save_name"],
                            "file_url": meta["file_url"],
                            "file_size": meta["file_size"],
                            "file_hash": meta["file_hash"],
                            "status": "success",
                            "msg": "上传成功，文件已存在（秒传）"
                        })
                        continue

                    os.makedirs(os.path.dirname(meta["save_path"]), exist_ok=True)
                    with open(meta["save_path"], "wb") as f:
                        f.write(meta["raw_content"])

                    new_record = FileRecord(
                        original_name=meta["original_name"],
                        save_name=meta["save_name"],
                        file_url=meta["file_url"],
                        file_size=meta["file_size"],
                        ext=meta["ext"],
                        file_hash=meta["file_hash"],
                        uploader_id=uploader_id
                    )
                    db_session.add(new_record)

                    result_list.append({
                        "original_name": meta["original_name"],
                        "save_name": meta["save_name"],
                        "file_url": meta["file_url"],
                        "file_size": meta["file_size"],
                        "file_hash": meta["file_hash"],
                        "status": "success",
                        "msg": "上传成功"
                    })

                db_session.commit()
                resp_data["data"] = result_list

    except Exception as e:
        db_session.rollback()
        current_app.logger.error(f"多文件上传异常:{e}")
        resp_data = {"code": 500, "msg": "上传失败", "error": str(e), "data": result_list}
        resp_code = 500
    finally:
        db_session.close()

    return jsonify(resp_data), resp_code# -------------------------- 接口2：大文件分块上传 --------------------------
@upload_bp.route("/chunk", methods=["POST"])
def chunk_upload():
    content_type = request.headers.get("Content-Type", "")
    if "boundary=" not in content_type:
        return jsonify({"code":400, "msg":"fei fa ge shi"}), 400
    boundary = content_type.split("boundary=")[-1]

    # 流式解析请求，大文件不会全量加载进内存
    headers = Headers([("Content-Type", f"multipart/form-data; boundary={boundary}")])
    parser = MultiPartParser(
        stream=request.stream,
        headers=headers,
        max_form_memory_size=0,
        cls=lambda *args: args[0]
    )

    upload_id = ""
    part_num = 0
    total_parts = 0
    file_hash = ""
    original_name = ""
    chunk_data = b""

    for field_name, value, filename, content_type in parser.parse():
        if field_name == "upload_id":
            upload_id = value.decode("utf-8")
        elif field_name == "part_num":
            part_num = int(value.decode("utf-8"))
        elif field_name == "total_parts":
            total_parts = int(value.decode("utf-8"))
        elif field_name == "file_hash":
            file_hash = value.decode("utf-8")
        elif field_name == "original_name":
            original_name = value.decode("utf-8")
        elif field_name == "chunk":
            chunk_data = value

    # 写入当前分片到临时目录
    temp_chunk_path = os.path.join(Config.CHUNK_TEMP_FOLDER, f"{upload_id}_part_{part_num}")
    with open(temp_chunk_path, "wb") as f:
        f.write(chunk_data)

    # 校验所有分片是否上传完成
    uploaded_chunks = os.listdir(Config.CHUNK_TEMP_FOLDER)
    current_uploaded = [p for p in uploaded_chunks if p.startswith(f"{upload_id}_part_")]

    if len(current_uploaded) == total_parts:
        # 秒传校验：文件哈希已存在直接返回，跳过合并
        exist_record = FileRecord.query.filter_by(file_hash=file_hash, is_deleted=False).first()
        if exist_record:
            # 清理临时分片
            for i in range(1, total_parts+1):
                os.unlink(os.path.join(Config.CHUNK_TEMP_FOLDER, f"{upload_id}_part_{i}"))
            return jsonify({"code":200, "msg":"success", "data":exist_record.to_dict()})

        # 合并所有分片
        ext = original_name.rsplit(".",1)[1].lower()
        save_name = generate_unique_save_name(ext)
        final_save_path = get_full_save_path(save_name)
        total_size = 0
        with open(final_save_path, "ab") as out_f:
            for i in range(1, total_parts+1):
                part_path = os.path.join(Config.CHUNK_TEMP_FOLDER, f"{upload_id}_part_{i}")
                with open(part_path, "rb") as in_f:
                    chunk = in_f.read()
                    total_size += len(chunk)
                    out_f.write(chunk)
                # 合并完成删除临时分片
                os.unlink(part_path)

        # 完整性校验
        with open(final_save_path, "rb") as f:
            calc_hash = hashlib.sha256(f.read()).hexdigest()
        if calc_hash != file_hash:
            os.unlink(final_save_path)
            return jsonify({"code":500, "msg":"file up faile  reload"}), 500

        # 写入数据库记录
        new_record = FileRecord(
            original_name = secure_filename(original_name),
            save_name = save_name,
            file_url = get_file_access_url(save_name),
            file_size = total_size,
            ext = ext,
            file_hash = file_hash,
            uploader_id = request.uid if hasattr(request, "uid") else 0
        )
        db.session.add(new_record)
        db.session.commit()
        return jsonify({"code":200, "msg":"da wen jian he bing wancheng", "data":new_record.to_dict()})

    return jsonify({"code":200, "msg":f"fen pian {part_num}shang chuan chenggong  dengdai qi ta ", "uploaded_count":len(current_uploaded), "total_count":total_parts})


 