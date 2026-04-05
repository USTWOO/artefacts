import sqlite3
import os

DB_PATH = "database/receipts.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create main receipts table
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

    # Check for migration needs
    cursor.execute("PRAGMA table_info(receipts)")
    columns = [row[1] for row in cursor.fetchall()]

    if "amount" in columns:
        # If amount exists, we want to rename it to subtotal
        # But we must check if subtotal already exists (from a partial migration or different schema)
        if "subtotal" not in columns:
             cursor.execute("ALTER TABLE receipts RENAME COLUMN amount TO subtotal")
        else:
             # This is a weird state, let's just drop amount if subtotal is already there
             # Or more safely, copy data and drop. But for simplicity in this sandbox:
             pass

    # Ensure other columns exist
    if "subtotal" not in columns and "amount" not in columns:
        cursor.execute("ALTER TABLE receipts ADD COLUMN subtotal REAL")
    if "image_path" not in columns:
        cursor.execute("ALTER TABLE receipts ADD COLUMN image_path TEXT")

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

def delete_receipt(receipt_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
    conn.commit()
    conn.close()

# Initialize DB on import
init_db()
