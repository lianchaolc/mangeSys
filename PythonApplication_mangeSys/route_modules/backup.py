#####2026.11.3 
###Ä¿µÄ¿ìÕÕ

#backup
from flask import Blueprint
import sqlite3
from datetime import datetime
import os

bp = Blueprint("backup", __name__)

@bp.get("/db/backup")
def db_backup():
    src_db = r"instance/crm.db"
    backup_dir = "backup"
    os.makedirs(backup_dir, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(backup_dir, f"crm_{now}.db")
    src_conn = sqlite3.connect(src_db)
    with sqlite3.connect(dst) as dst_conn:
        src_conn.backup(dst_conn)
    src_conn.close()
    return {"msg":"success savesqldata", "file":dst}
