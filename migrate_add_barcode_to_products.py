#!/usr/bin/env python3
import sqlite3
import os

DB_PATH = 'pos_tailor.db'

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found: {DB_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA table_info(products)")
        cols = [row[1] for row in cur.fetchall()]
        if 'barcode' in cols:
            print('barcode column already exists')
        else:
            print('Adding barcode column to products...')
            cur.execute("ALTER TABLE products ADD COLUMN barcode TEXT")
            print('Creating index on products(barcode,user_id)...')
            cur.execute("CREATE INDEX IF NOT EXISTS idx_products_user_barcode ON products(user_id, barcode)")
            conn.commit()
            print('Done')
    finally:
        conn.close()

if __name__ == '__main__':
    main()
