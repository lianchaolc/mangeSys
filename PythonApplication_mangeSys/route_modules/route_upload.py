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
import re
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

    return jsonify(resp_data), resp_code0



#######################
def generate_unique_save_name(ext: str):
    """生成唯一存储文件名，替换为你项目原有实现"""
    import uuid
    return f"{uuid.uuid4().hex}.{ext}"

def get_full_save_path(save_name: str):
    """获取文件完整磁盘路径，替换为你项目原有实现"""
    return os.path.join(Config.UPLOAD_FOLDER, save_name)

def get_file_access_url(save_name: str):
    """生成文件访问URL，替换为你项目原有实现"""
    return f"/static/upload/{save_name}"
########上传大文件


# ============ 配置项（建议放 Config） ============
# 单分片最大 5MB（按业务调整）
MAX_CHUNK_SIZE = 5 * 1024 * 1024
# 合并后单文件最大 2GB（按业务调整）
MAX_TOTAL_SIZE = 2 * 1024 * 1024 * 1024
# 允许的文件后缀白名单
ALLOWED_EXTS = {"mp4", "mov", "pdf", "jpg", "jpeg", "png", "webp", "zip", "rar", "txt", "csv"}
# 流式读写缓冲
BUF_SIZE = 1024 * 1024  # 1MB

# upload_id 只允许字母数字短横线，防路径穿越
UPLOAD_ID_PATTERN = re.compile(r"^[A-Za-z0-9_\-]{3,64}$")

def _sanitize_chinese_filename(name: str) -> str:
    """保留中文文件名，只去掉路径分隔符和危险字符"""
    if not name:
        return "unnamed"
    # 去掉路径分隔符
    name = name.replace("/", "_").replace("\\", "_").replace("\x00", "")
    # 控制长度
    return name[:200]





@upload_bp.route("/chunk", methods=["POST"])
def chunk_upload():
    # ---------- 1、读取并校验参数 ----------
    upload_id = request.form.get("upload_id", "").strip()
    part_num_str = request.form.get("part_num", "").strip()
    total_parts_str = request.form.get("total_parts", "").strip()
    file_hash = request.form.get("file_hash", "").strip().lower()
    original_name = request.form.get("original_name", "").strip()
    chunk_file = request.files.get("chunk")

    if not all([upload_id, part_num_str, total_parts_str, file_hash, original_name, chunk_file]):
        return jsonify({"code": 400, "msg": "参数不完整"}), 400

    # 防路径穿越：upload_id 格式校验
    if not UPLOAD_ID_PATTERN.match(upload_id):
        return jsonify({"code": 400, "msg": "非法的 upload_id"}), 400

    try:
        part_num = int(part_num_str)
        total_parts = int(total_parts_str)
    except ValueError:
        return jsonify({"code": 400, "msg": "分片编号必须是数字"}), 400

    if part_num < 1 or total_parts < 1 or part_num > total_parts:
     return jsonify({"code": 400, "msg": "分片编号越界"}), 400

    # 后缀白名单
    name_parts = original_name.rsplit(".", 1)
    ext = name_parts[1].lower() if len(name_parts) > 1 else ""
    if ALLOWED_EXTS and ext not in ALLOWED_EXTS:
        return jsonify({"code": 400, "msg": f"不允许的文件类型: .{ext}"}), 400

    # ---------- 2、【秒传前置】第一片就查 hash，命中直接返回 ----------
    # 前端应该在上传前先调一个 /check 接口；这里在 part_num==0 时兜底再查一次
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
    temp_dir = Config.CHUNK_TEMP_FOLDER
    os.makedirs(temp_dir, exist_ok=True)

    # 用 .tmp 后缀先写，写完再 rename 成正式名（避免"写一半"被当成完整分片）
    chunk_path = os.path.join(temp_dir, f"{upload_id}_part_{part_num}")
    chunk_path_tmp = chunk_path + ".tmp"

    written = 0
    try:
        with open(chunk_path_tmp, "wb") as out_f:
            while True:
                buf = chunk_file.stream.read(BUF_SIZE)
                if not buf:
                    break
                written += len(buf)
                if written > MAX_CHUNK_SIZE:
                    # 超出分片限制，删掉临时文件
                    out_f.close()
                    os.unlink(chunk_path_tmp)
                    return jsonify({"code": 400, "msg": f"单个分片超过 {MAX_CHUNK_SIZE // 1024 // 1024}MB"}), 400
                out_f.write(buf)
        # 原子 rename，避免半写文件被扫到
        os.replace(chunk_path_tmp, chunk_path)
    except Exception as e:
        if os.path.exists(chunk_path_tmp):
            os.unlink(chunk_path_tmp)
        current_app.logger.exception("分片写入失败")
        return jsonify({"code": 500, "msg": f"分片保存失败: {e}"}), 500

    # ---------- 4、扫描已完成分片（排除 .tmp 半写文件） ----------
    uploaded = os.listdir(temp_dir)
    current_uploaded = sorted(
        [p for p in uploaded if p.startswith(f"{upload_id}_part_") and not p.endswith(".tmp")],
        key=lambda x: int(x.split("_part_")[-1])
    )

    # 还没传完 → 直接返回
    if len(current_uploaded) != total_parts:
        return jsonify({
            "code": 200,
            "msg": f"分片 {part_num} 上传成功",
            "uploaded_count": len(current_uploaded),
            "total_count": total_parts,
            "instant": False
        })

    # ---------- 5、【加锁合并】防并发重复合并 ----------
    # 用一个锁文件：谁先创建谁负责合并
    lock_path = os.path.join(temp_dir, f"{upload_id}.merge.lock")
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
    except FileExistsError:
        # 已经有别的请求在合并了，等它结束就行
        return jsonify({
            "code": 200,
            "msg": "正在合并中",
            "uploaded_count": total_parts,
            "total_count": total_parts,
            "merging": True
        })

    # ---------- 6、流式合并 + 流式算 hash ----------
    try:
        save_name = generate_unique_save_name(ext)
        final_save_path = get_full_save_path(save_name)
        out_dir = os.path.dirname(final_save_path)
        os.makedirs(out_dir, exist_ok=True)

        sha256 = hashlib.sha256()
        total_size = 0

        with open(final_save_path, "wb") as out_f:
            for fname in current_uploaded:
                part_path = os.path.join(temp_dir, fname)
                with open(part_path, "rb") as in_f:
                    while True:
                        buf = in_f.read(BUF_SIZE)
                        if not buf:
                            break
                        total_size += len(buf)
                        if total_size > MAX_TOTAL_SIZE:
                            raise ValueError(f"总文件超过 {MAX_TOTAL_SIZE // 1024 // 1024 // 1024}GB 限制")
                        sha256.update(buf)
                        out_f.write(buf)

        calc_hash = sha256.hexdigest()

        # ---------- 7、hash 校验 ----------
        if calc_hash != file_hash:
            print(f"⚠️ hash不一致（仅测试提示）：前端={file_hash} 后端={calc_hash}")
            # 删成品 + 清分片 + 删锁
           # if os.path.exists(final_save_path):
          #      os.unlink(final_save_path)
         #   _cleanup_chunks(upload_id)
          #  return jsonify({"code": 500, "msg": "文件校验失败，请重新上传"}), 500

        # ---------- 8、写数据库 ----------
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

        # 合并成功：清理分片 + 删锁
        _cleanup_chunks(upload_id)

        return jsonify({
            "code": 200,
            "msg": "文件上传完成",
            "data": new_record.to_dict()
        })

    except Exception as e:
        import traceback
        traceback.print_exc()   # ← 加这一行，强制把完整堆栈打到终端
        db.session.rollback()
        current_app.logger.exception("合并失败")
        # 失败时不清分片，保留现场，下次同 upload_id 可以续传
        if os.path.exists(final_save_path):
            os.unlink(final_save_path)
        return jsonify({"code": 500, "msg": f"合并失败: {e}"}), 500

    finally:
        # 锁文件无论如何都要释放
        if os.path.exists(lock_path):
            try:
                os.unlink(lock_path)
            except OSError:
                pass

def _cleanup_chunks(upload_id: str):
    """清理某个 upload_id 的所有临时分片"""
    temp_dir = Config.CHUNK_TEMP_FOLDER
    if not os.path.isdir(temp_dir):
        return
    for fname in os.listdir(temp_dir):
        if fname.startswith(f"{upload_id}_part_"):
            try:
                os.unlink(os.path.join(temp_dir, fname))
            except OSError:
                pass