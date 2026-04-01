import sqlite3
import os

DB_PATH = "receipts.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT,
            date TEXT,
            subtotal REAL,
            vat REAL,
            total REAL,
            category TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_receipt(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO receipts (vendor, date, subtotal, vat, total, category, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("vendor"),
        data.get("date"),
        data.get("subtotal"),
        data.get("vat"),
        data.get("total"),
        data.get("category"),
        data.get("image_path")
    ))
    conn.commit()
    conn.close()

def get_receipts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM receipts ORDER BY id DESC")
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    conn.close()
    return results

def get_monthly_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            substr(date, 1, 7) as month,
            SUM(total) as total_expense,
            SUM(vat) as total_vat
        FROM receipts
        GROUP BY month
        ORDER BY month DESC
    """)
    results = [{"month": r[0], "total_expense": r[1], "total_vat": r[2]} for r in cursor.fetchall()]
    conn.close()
    return results

def get_category_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            category,
            SUM(total) as total_expense,
            SUM(vat) as total_vat
        FROM receipts
        GROUP BY category
        ORDER BY total_expense DESC
    """)
    results = [{"category": r[0], "total_expense": r[1], "total_vat": r[2]} for r in cursor.fetchall()]
    conn.close()
    return results

init_db()
