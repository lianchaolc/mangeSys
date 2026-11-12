# -*- coding: utf-8 -*-
from app import app, db
from sqlalchemy import text

with app.app_context():
    sql = text("ALTER TABLE org ADD COLUMN branch_code VARCHAR(64);")
    db.session.execute(sql)
    db.session.commit()
    print("Done, column added.")
