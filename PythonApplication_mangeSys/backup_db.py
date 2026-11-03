###案 A：**独立脚本 + Windows 任务计划程序（最推荐，简单稳定，不依赖 Flask 服务是否运行）**
###✅ 方案 A（优先选这个）：单独备份脚本，Windows 任务计划跑
import sqlite3
from datetime import datetime
import os

# 数据库路径，建议写绝对路径，避免定时任务工作目录错乱
src_db = r"D:\pythson\pro\PythonApplication_mangeSys\PythonApplication_mangeSys\instance\crm.db"
backup_dir = r"D:\pythson\pro\PythonApplication_mangeSys\PythonApplication_mangeSys\backup"

os.makedirs(backup_dir, exist_ok=True)

now = datetime.now().strftime("%Y%m%d_%H%M%S")
dst_path = os.path.join(backup_dir, f"crm_snapshot_{now}.db")

# SQLite官方在线备份
src_conn = sqlite3.connect(src_db)
with sqlite3.connect(dst_path) as dst_conn:
    src_conn.backup(dst_conn)
src_conn.close()

print(f"✅ 备份完成：{dst_path}")

# 【可选】自动清理：只保留最近7天的备份，删掉更早的
import time
keep_days = 7
cutoff = time.time() - keep_days * 86400
for fname in os.listdir(backup_dir):
    full_path = os.path.join(backup_dir, fname)
    if os.path.isfile(full_path) and fname.startswith("crm_snapshot_"):
        if os.path.getmtime(full_path) < cutoff:
            os.remove(full_path)
            print(f"🗑 删除旧备份：{fname}")
