#!/usr/bin/env python3
"""
Sample Data Generator for Tailor POS (SQLite)

Generates realistic Middle Eastern data for a specific user (default user_id=2):
 - Product types and products (derived from provided domain list)
 - Employees (7 by default)
 - Customers (100 by default)
 - Invoices/Bills (1000 by default) over the last 6 months with 70/30 Paid/Pending

This script is idempotent per run when using --reset. Without --reset, it will
only add missing product types/products and then append employees/customers/bills.

Safety:
 - Mobile numbers are normalized to digits (9–10 digits). UAE-style 10-digit numbers are used.
 - Bill numbers are unique per user via BILL-YYYYMMDD-XXX.

Usage examples:
  python generate_sample_data.py --user_id 2 --reset
  python generate_sample_data.py --user_id 2 --num_customers 100 --num_bills 1000
"""

from __future__ import annotations

import argparse
import os
import random
import sqlite3
import string
import uuid
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple

DB_PATH = os.environ.get("TAILOR_POS_DB", "pos_tailor.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


PRODUCT_DEFINITIONS = {
    # name -> rate (AED). We will classify each into a product type
    "Saree fall stitching with fall fabric": 30,
    "Saree petticoat stitching": 40,
    "Kurti (no lining)": 55,
    "Kurti with lining": 75,
    "Palazzo no lining": 80,
    "Trouser or pant no lining": 80,
    "Shirt": 100,
    "Salwar suit no lining": 100,
    "Trousers pants with lining": 100,
    "Kaftan no lining": 100,
    "Palazzo with lining": 105,
    "Saree belt stitching": 150,
    "Pant suits palazzo suit no lining": 110,
    "Blouse non padded": 115,
    "Salwar suit half / top lining": 115,
    "Patiala suit no lining": 125,
    "Salwar suit with full lining": 125,
    "Kaftan with lining": 125,
    "Pant suit Palazzo suit top / half lining": 125,
    "Abaya stitching": 125,
    "Pant suits palazzo suit with full lining": 135,
    "Patiala suit with half / top lining": 140,
    "Blouse padded": 150,
    "Patiala suit with lining": 150,
    "Anarkali (8 kaliyan)": 160,
    "Gown stitching": 150,
    "Jump suit": 170,
    "Lehenga stitching": 195,
    "Designer one piece": 195,
    "Designer Blouse": 150,
    "Sharara/Gharara with kurti": 240,
    "Lehenga choli": 320,
    "Coat / Blazer": 350,
    "Coat pant / suit 2 piece": 450,
    "Dress indo western": 150,
    "Dress western": 225,
}


def classify_product_type(product_name: str) -> str:
    name = product_name.lower()
    # Simple keyword-based classification
    mapping = [
        ("saree", "Saree"),
        ("kurti", "Kurti"),
        ("palazzo", "Palazzo"),
        ("trouser", "Trousers"),
        ("pant suit", "Pant Suit"),
        ("pant suits", "Pant Suit"),
        ("pants", "Trousers"),
        ("shirt", "Shirt"),
        ("salwar", "Salwar Suit"),
        ("patiala", "Patiala Suit"),
        ("kaftan", "Kaftan"),
        ("blouse", "Blouse"),
        ("abaya", "Abaya"),
        ("anarkali", "Anarkali"),
        ("gown", "Gown"),
        ("jump", "Jump Suit"),
        ("lehenga choli", "Lehenga Choli"),
        ("lehenga", "Lehenga"),
        ("designer", "Designer"),
        ("sharara", "Sharara/Gharara"),
        ("gharara", "Sharara/Gharara"),
        ("coat pant", "Suit"),
        ("coat / blazer", "Blazer"),
        ("blazer", "Blazer"),
        ("suit", "Suit"),
        ("indo western", "Indo Western"),
        ("western", "Western"),
        ("belt", "Accessories"),
    ]
    for key, type_name in mapping:
        if key in name:
            return type_name
    return "Tailoring"


FIRST_NAMES = [
    "Ahmed", "Mohammed", "Hassan", "Omar", "Yousef", "Khalid", "Abdullah", "Hamza", "Fahad", "Sami",
    "Ali", "Bilal", "Imran", "Ibrahim", "Mustafa", "Ziad", "Amir", "Nasser", "Karim", "Majid",
]
LAST_NAMES = [
    "Al Mansoori", "Al Falasi", "Al Maktoum", "Al Nahyan", "Al Qasimi", "Al Nuaimi", "Al Mualla",
    "Al Sharqi", "Al Hammadi", "Al Suwaidi", "Al Hosani", "Al Zaabi", "Al Marri", "Al Balushi",
]


def random_phone() -> str:
    # UAE-style 050/052/054 + 7 digits => 10 digits total
    prefix = random.choice(["050", "052", "054", "056", "058"])
    return prefix + ''.join(random.choices(string.digits, k=7))


def pick_cities_and_areas(conn: sqlite3.Connection) -> Tuple[List[str], Dict[str, List[str]]]:
    cities: List[str] = []
    areas_by_city: Dict[str, List[str]] = defaultdict(list)
    try:
        for row in conn.execute("SELECT city_name FROM cities ORDER BY city_name"):
            cities.append(row[0])
        for row in conn.execute(
            "SELECT c.city_name, a.area_name FROM city_area a JOIN cities c ON a.city_id = c.city_id"
        ):
            areas_by_city[row[0]].append(row[1])
    except Exception:
        # Fallbacks
        cities = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"]
        areas_by_city["Dubai"] = [
            "Deira", "Bur Dubai", "Al Barsha", "Karama", "Mirdif", "JLT", "JVC", "Marina", "Satwa"
        ]
    return cities, areas_by_city


def ensure_product_types_and_products(conn: sqlite3.Connection, user_id: int) -> Dict[str, int]:
    # Create or fetch product types
    type_name_to_id: Dict[str, int] = {}
    for product_name in PRODUCT_DEFINITIONS:
        type_name = classify_product_type(product_name)
        # Insert type if missing
        cur = conn.execute(
            "SELECT type_id FROM product_types WHERE user_id = ? AND type_name = ?",
            (user_id, type_name),
        ).fetchone()
        if cur is None:
            conn.execute(
                "INSERT INTO product_types (user_id, type_name) VALUES (?, ?)",
                (user_id, type_name),
            )
    conn.commit()

    for row in conn.execute("SELECT type_id, type_name FROM product_types WHERE user_id = ?", (user_id,)):
        type_name_to_id[row[1]] = row[0]

    # Create products under those types
    for product_name, rate in PRODUCT_DEFINITIONS.items():
        type_name = classify_product_type(product_name)
        type_id = type_name_to_id[type_name]
        exists = conn.execute(
            "SELECT 1 FROM products WHERE user_id = ? AND product_name = ?",
            (user_id, product_name),
        ).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO products (user_id, type_id, product_name, rate, is_active) VALUES (?, ?, ?, ?, 1)",
                (user_id, type_id, product_name, float(rate)),
            )
    conn.commit()
    return type_name_to_id


def create_employees(conn: sqlite3.Connection, user_id: int, count: int = 7) -> List[int]:
    roles = ["Tailor", "Tailor", "Tailor", "Manager", "Cutter", "Stitcher", "Ironing"]
    employee_ids: List[int] = []
    existing = conn.execute("SELECT employee_id FROM employees WHERE user_id = ?", (user_id,)).fetchall()
    if len(existing) >= count:
        return [r[0] for r in existing[:count]]
    for i in range(count - len(existing)):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        phone = random_phone()
        role = roles[i % len(roles)]
        address = random.choice(["Dubai", "Sharjah", "Abu Dhabi"]) + ", UAE"
        conn.execute(
            "INSERT INTO employees (user_id, name, phone, address, position) VALUES (?, ?, ?, ?, ?)",
            (user_id, name, phone, address, role),
        )
    conn.commit()
    for row in conn.execute("SELECT employee_id FROM employees WHERE user_id = ?", (user_id,)):
        employee_ids.append(row[0])
    return employee_ids[:count]


def create_customers(conn: sqlite3.Connection, user_id: int, count: int = 100) -> List[int]:
    cities, areas_by_city = pick_cities_and_areas(conn)
    customer_ids: List[int] = []
    existing = conn.execute("SELECT customer_id FROM customers WHERE user_id = ?", (user_id,)).fetchall()
    base = len(existing)
    for i in range(count):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        phone = random_phone()
        city = random.choice(cities)
        area_list = areas_by_city.get(city) or []
        area = random.choice(area_list) if area_list else ""
        # Avoid duplicate mobile
        dup = conn.execute(
            "SELECT 1 FROM customers WHERE user_id = ? AND phone = ?", (user_id, phone)
        ).fetchone()
        if dup:
            continue
        conn.execute(
            """
            INSERT INTO customers (user_id, name, phone, city, area, customer_type)
            VALUES (?, ?, ?, ?, ?, 'Individual')
            """,
            (user_id, name, phone, city, area),
        )
    conn.commit()
    for row in conn.execute("SELECT customer_id FROM customers WHERE user_id = ?", (user_id,)):
        customer_ids.append(row[0])
    # Return only newly created (approx):
    return customer_ids[base:]


def get_products(conn: sqlite3.Connection, user_id: int) -> List[sqlite3.Row]:
    return conn.execute(
        "SELECT product_id, product_name, rate, type_id FROM products WHERE user_id = ? AND is_active = 1",
        (user_id,),
    ).fetchall()


def generate_bill_number(existing: set, bill_date: date, seq_by_date: Dict[str, int], user_id: int) -> str:
    ymd = bill_date.strftime("%Y%m%d")
    seq_by_date.setdefault(ymd, 0)
    seq_by_date[ymd] += 1
    bill_num = f"BILL-{ymd}-{seq_by_date[ymd]:03d}"
    # Ensure uniqueness within this run (DB has unique constraint per user)
    while bill_num in existing:
        seq_by_date[ymd] += 1
        bill_num = f"BILL-{ymd}-{seq_by_date[ymd]:03d}"
    existing.add(bill_num)
    return bill_num


def create_bills(
    conn: sqlite3.Connection,
    user_id: int,
    num_bills: int,
    employee_ids: List[int],
    bias_employee_ids: List[int],
    bias_customer_ids: List[int],
):
    products = get_products(conn, user_id)
    if not products:
        raise RuntimeError("No products found. Ensure products were created before bills.")

    # Bias product popularity: weight certain keywords to show trending
    def product_weight(pname: str) -> int:
        pname_l = pname.lower()
        if any(k in pname_l for k in ["kurti", "palazzo", "salwar", "blouse"]):
            return 5
        if any(k in pname_l for k in ["lehenga", "designer", "coat", "blazer"]):
            return 3
        return 1

    product_choices = [(p, product_weight(p["product_name"])) for p in products]
    # Expand into weighted list for simplicity
    weighted_products: List[sqlite3.Row] = []
    for p, w in product_choices:
        weighted_products.extend([p] * w)

    customers = conn.execute(
        "SELECT customer_id, name, phone, city, area FROM customers WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    if not customers:
        raise RuntimeError("No customers found. Generate customers first.")

    # Weighted employees and customers for bias
    all_emp_choices = employee_ids + bias_employee_ids * 3
    all_cust_choices = [c["customer_id"] for c in customers] + bias_customer_ids * 3

    existing_bill_numbers = set()
    seq_by_date: Dict[str, int] = {}

    vat_percent = 5.0
    start_date = date.today() - timedelta(days=180)

    for i in range(num_bills):
        bill_dt = start_date + timedelta(days=random.randint(0, 180))
        delivery_dt = bill_dt + timedelta(days=random.randint(1, 7))
        bill_num = generate_bill_number(existing_bill_numbers, bill_dt, seq_by_date, user_id)
        bill_uuid = str(uuid.uuid4())

        cust_id = random.choice(all_cust_choices)
        cust = next(c for c in customers if c["customer_id"] == cust_id)
        emp_id = random.choice(all_emp_choices)

        # Pick 1-4 items biased by weighted_products
        num_items = random.choices([1, 2, 3, 4], weights=[40, 35, 20, 5])[0]
        items = random.sample(weighted_products, k=num_items)
        subtotal = 0.0
        bill_items_payload: List[Tuple] = []
        for item in items:
            qty = random.choices([1, 2, 3], weights=[80, 18, 2])[0]
            rate = float(item["rate"])
            discount = 0.0
            line_sub = (rate * qty) - discount
            vat_amt = line_sub * (vat_percent / 100)
            line_total = line_sub + vat_amt
            subtotal += line_sub
            bill_items_payload.append(
                (
                    user_id,
                    None,  # placeholder for bill_id
                    item["product_id"],
                    item["product_name"],
                    qty,
                    rate,
                    discount,
                    vat_amt,
                    0.0,
                    line_total,
                )
            )

        vat_amount = subtotal * (vat_percent / 100)
        total_amount = subtotal + vat_amount

        is_paid = random.random() < 0.70  # 70% paid
        if is_paid:
            advance_paid = total_amount
            balance_amount = 0.0
            status = "Paid"
        else:
            advance_paid = round(total_amount * random.uniform(0.0, 0.7), 2)
            balance_amount = round(total_amount - advance_paid, 2)
            status = "Pending"

        conn.execute(
            """
            INSERT INTO bills (
                user_id, bill_number, customer_id, customer_name, customer_phone,
                customer_city, customer_area, customer_trn, uuid, bill_date, delivery_date,
                payment_method, subtotal, vat_amount, total_amount, advance_paid, balance_amount,
                status, master_id, trial_date, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Cash', ?, ?, ?, ?, ?, ?, ?, NULL, NULL)
            """,
            (
                user_id,
                bill_num,
                cust["customer_id"],
                cust["name"],
                cust["phone"],
                cust["city"],
                cust["area"],
                "",
                bill_uuid,
                bill_dt.strftime("%Y-%m-%d"),
                delivery_dt.strftime("%Y-%m-%d"),
                subtotal,
                vat_amount,
                total_amount,
                advance_paid,
                balance_amount,
                status,
                emp_id,
            ),
        )
        bill_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        # Insert bill items
        for payload in bill_items_payload:
            conn.execute(
                """
                INSERT INTO bill_items (
                    user_id, bill_id, product_id, product_name, quantity,
                    rate, discount, vat_amount, advance_paid, total_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (payload[0], bill_id) + payload[2:],
            )

    conn.commit()


def reset_user_data(conn: sqlite3.Connection, user_id: int) -> None:
    # Danger: remove user-specific data to make script idempotent
    tables = [
        "bill_items",
        "bills",
        "employees",
        "customers",
        "products",
        "product_types",
    ]
    for t in tables:
        conn.execute(f"DELETE FROM {t} WHERE user_id = ?", (user_id,))
    conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Generate realistic sample data for Tailor POS")
    parser.add_argument("--user_id", type=int, default=2)
    parser.add_argument("--num_employees", type=int, default=7)
    parser.add_argument("--num_customers", type=int, default=100)
    parser.add_argument("--num_bills", type=int, default=1000)
    parser.add_argument("--reset", action="store_true", help="Delete existing user data before seeding")
    args = parser.parse_args()

    conn = get_conn()
    try:
        if args.reset:
            print(f"Resetting user data for user_id={args.user_id} ...")
            reset_user_data(conn, args.user_id)

        print("Creating product types and products ...")
        ensure_product_types_and_products(conn, args.user_id)

        print("Creating employees ...")
        employee_ids = create_employees(conn, args.user_id, args.num_employees)

        print("Creating customers ...")
        new_customer_ids = create_customers(conn, args.user_id, args.num_customers)

        # Bias: favor first few employees and customers
        bias_emp = employee_ids[:3] if len(employee_ids) >= 3 else employee_ids
        # If new customers are less than requested, still pick bias from current pool
        all_customer_ids = [row[0] for row in conn.execute(
            "SELECT customer_id FROM customers WHERE user_id = ?", (args.user_id,)
        ).fetchall()]
        bias_cust = all_customer_ids[:3] if len(all_customer_ids) >= 3 else all_customer_ids

        print("Creating bills (this may take a moment) ...")
        create_bills(conn, args.user_id, args.num_bills, employee_ids, bias_emp, bias_cust)

        print("Done. Sample data generated successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()


