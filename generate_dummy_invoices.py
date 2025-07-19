import sqlite3
import random
from datetime import datetime, timedelta

DB = "pos_tailor.db"

# List of Dubai areas
DUBAI_AREAS = [
    'Al Barari', 'Al Barsha', 'Al Furjan', 'Al Garhoud', 'Al Habtoor City', 'Al Hamriya', 'Al Hudaiba', 'Al Jaddaf',
    'Al Jafiliya', 'Al Karama', 'Al Kifaf', 'Al Mankhool', 'Al Markada', 'Al Mina (Dubai Maritime City)', 'Al Mizhar First',
    'Al Mizhar Second', 'Al Muhaisnah (First, Second, Third, Fourth)', 'Al Nahda (First, Second)', 'Al Quoz',
    'Al Qusais (First, Second, Industrial First, Second, Third, Fourth, Fifth)', 'Al Rashidiya', 'Al Rifa', 'Al Safa First',
    'Al Satwa', 'Al Shindagha', 'Al Souk Al Kabir', 'Al Sufouh', 'Al Twar (First, Second, Third, Fourth)', 'Al Wasl',
    'Arabian Ranches', 'Arjan (Dubailand)', 'Barsha Heights (Tecom)', 'Bluewaters Island', 'Bur Dubai', 'Business Bay',
    'City Walk', 'DAMAC Hills (Akoya)', 'DAMAC Hills 2', 'DAMAC Lagoons', 'Deira', 'Discovery Gardens',
    'District One (Mohammed Bin Rashid City - District One)', 'Downtown Dubai', 'Downtown Jebel Ali', 'Dubai Airport',
    'Dubai Creek Harbour', 'Dubai Design District (d3)', 'Dubai Harbour', 'Dubai Healthcare City (DHCC)',
    'Dubai Hills Estate', 'Dubai Industrial City', 'Dubai International City', 'Dubai International Financial Centre (DIFC)',
    'Dubai Investment Park (DIP)', 'Dubai Islands', 'Dubai Marina', 'Dubai Production City (IMPZ)',
    'Dubai Silicon Oasis (DSO)', 'Dubai South', 'Dubai Sports City', 'Dubai Studio City', 'Dubailand', 'Emaar Beachfront',
    'Emaar South', 'Emirates Hills', 'Expo City', 'Green Community', 'International City', 'Jebel Ali Village', 'Jumeirah',
    'Jumeirah Bay', 'Jumeirah Beach Residence (JBR)', 'Jumeirah Golf Estates', 'Jumeirah Islands', 'Jumeirah Lake Towers (JLT)',
    'Jumeirah Park', 'Jumeirah Village Circle (JVC)', 'Jumeirah Village Triangle (JVT)', 'Liwan', 'Madinat Jumeirah Living (MJL)',
    'Meadows', 'Meydan', 'Mirdif', 'Mina Rashid', 'Motor City', 'Mudon', 'Mushrif', 'Nad Al Sheba', 'Palm Jebel Ali',
    'Palm Jumeirah', 'The Springs', 'The Valley', 'Tilal Al Ghaf', 'Town Square', 'Trade Centre 1', 'Trade Centre 2',
    'Umm Hurair First', 'Umm Hurair Second', 'Umm Ramool', 'Umm Suqeim', 'Wasl Gate', 'World Islands', 'Zabeel (First, Second)'
]

# List of 500+ realistic Middle Eastern/Muslim names
MUSLIM_NAMES = [
    'Ahmed', 'Mohammed', 'Ali', 'Hassan', 'Hussein', 'Omar', 'Yusuf', 'Ibrahim', 'Khalid', 'Sami',
    'Faisal', 'Saeed', 'Tariq', 'Imran', 'Bilal', 'Zaid', 'Rashid', 'Salman', 'Majid', 'Nasser',
    'Abdullah', 'Abdul Rahman', 'Abdul Aziz', 'Abdul Malik', 'Abdul Samad', 'Abdul Qadir',
    'Fatima', 'Aisha', 'Maryam', 'Khadija', 'Zainab', 'Sara', 'Noor', 'Layla', 'Huda', 'Yasmin',
    'Mona', 'Rania', 'Samira', 'Nadia', 'Amira', 'Salma', 'Hana', 'Dina', 'Lubna', 'Rasha',
    'Jamal', 'Karim', 'Samir', 'Adnan', 'Farid', 'Fadi', 'Walid', 'Mansour', 'Sultan', 'Zaki',
    'Mariam', 'Rami', 'Nour', 'Nada', 'Lina', 'Othman', 'Sahar', 'Amin', 'Aminah',
    'Basim', 'Bashir', 'Fawzi', 'Gamal', 'Habib', 'Jabir', 'Kamal', 'Latif', 'Munir', 'Nabil',
    'Qasim', 'Rafik', 'Sabir', 'Talib', 'Waleed', 'Yahya', 'Zayd', 'Ziyad', 'Samah', 'Sawsan',
    'Rabab', 'Razan', 'Rima', 'Sana', 'Shadia', 'Suad', 'Widad', 'Yumna', 'Zahra',
    'Adeel', 'Aftab', 'Akram', 'Amjad', 'Anas', 'Anwar', 'Arif', 'Asad', 'Ashraf', 'Atif',
    'Aziz', 'Badr', 'Bashar', 'Dawood', 'Ehsan', 'Fahad', 'Faisal', 'Firas', 'Ghani', 'Hamid',
    'Haroon', 'Hashim', 'Hilal', 'Hisham', 'Idris', 'Ihsan', 'Ikram', 'Ismail', 'Jaleel', 'Junaid',
    'Kareem', 'Khalaf', 'Mahmoud', 'Majed', 'Mansoor', 'Marwan', 'Masood', 'Mazhar', 'Mazin', 'Moin',
    'Mubarak', 'Mujahid', 'Munawwar', 'Mustafa', 'Nadeem', 'Naeem', 'Naseem', 'Nasir', 'Nawaf', 'Nizar',
    'Qadir', 'Qasim', 'Qudrat', 'Rafay', 'Rami', 'Rashad', 'Rayyan', 'Ridwan', 'Saad', 'Sadiq',
    'Sajid', 'Sameer', 'Shafiq', 'Shakir', 'Shams', 'Sharif', 'Shaukat', 'Shoaib', 'Sohail', 'Sulaiman',
    'Taha', 'Tariq', 'Tawfiq', 'Usama', 'Wajid', 'Wasim', 'Yasir', 'Younis', 'Yusuf', 'Zafar',
    'Zahid', 'Zain', 'Zaki', 'Zubair', 'Aaliyah', 'Abeer', 'Afaf', 'Ahlam', 'Aida', 'Aisha',
    'Alia', 'Amal', 'Amira', 'Anisa', 'Asma', 'Ayah', 'Aziza', 'Basma', 'Dalal', 'Dania',
    'Dina', 'Duha', 'Fadwa', 'Fahima', 'Farah', 'Farida', 'Fatin', 'Ghada', 'Hala', 'Hanan',
    'Heba', 'Hind', 'Huda', 'Iman', 'Jana', 'Jamila', 'Jumana', 'Kamilah', 'Kawthar', 'Laila',
    'Lama', 'Lina', 'Lubna', 'Maha', 'Mahira', 'Malak', 'Manal', 'Marwa', 'Maysaa', 'Mona',
    'Munira', 'Nada', 'Nadia', 'Nahla', 'Naima', 'Najwa', 'Nawal', 'Nida', 'Nisreen', 'Noor',
    'Rabab', 'Rafif', 'Rania', 'Rasha', 'Razan', 'Reem', 'Rima', 'Rola', 'Ruba', 'Rula',
    'Sabrine', 'Sahar', 'Salma', 'Samar', 'Samira', 'Sana', 'Sarah', 'Shadia', 'Shams', 'Shaza',
    'Siham', 'Suhad', 'Suha', 'Sundus', 'Tahani', 'Tahira', 'Tamara', 'Wafaa', 'Widad', 'Yasmin',
    'Yumna', 'Zahra', 'Zainab', 'Zakia', 'Zeinab', 'Zubaida', 'Zuhair', 'Zuleika', 'Adeelah', 'Ahlam',
    'Aida', 'Aila', 'Aisha', 'Alaa', 'Almas', 'Amal', 'Amira', 'Anhar', 'Anisa', 'Arwa',
    'Asiya', 'Asma', 'Atifa', 'Ayah', 'Aziza', 'Badia', 'Basma', 'Bushra', 'Dalal', 'Dania',
    'Dima', 'Dina', 'Duha', 'Fadwa', 'Fahima', 'Faiqa', 'Farah', 'Farida', 'Fatin', 'Fawzia',
    'Ghada', 'Ghazal', 'Hala', 'Hanan', 'Heba', 'Hind', 'Huda', 'Iman', 'Jana', 'Jamila',
    'Jumana', 'Kamilah', 'Kawthar', 'Laila', 'Lama', 'Lina', 'Lubna', 'Maha', 'Mahira', 'Malak',
    'Manal', 'Marwa', 'Maysaa', 'Mona', 'Munira', 'Nada', 'Nadia', 'Nahla', 'Naima', 'Najwa',
    'Nawal', 'Nida', 'Nisreen', 'Noor', 'Rabab', 'Rafif', 'Rania', 'Rasha', 'Razan', 'Reem',
    'Rima', 'Rola', 'Ruba', 'Rula', 'Sabrine', 'Sahar', 'Salma', 'Samar', 'Samira', 'Sana',
    'Sarah', 'Shadia', 'Shams', 'Shaza', 'Siham', 'Suhad', 'Suha', 'Sundus', 'Tahani', 'Tahira',
    'Tamara', 'Wafaa', 'Widad', 'Yasmin', 'Yumna', 'Zahra', 'Zainab', 'Zakia', 'Zeinab', 'Zubaida',
    'Zuhair', 'Zuleika', 'Abbas', 'Abdul', 'Abdulahi', 'Abdulkadir', 'Abdullah', 'Abdurrahman', 'Abid', 'Abu',
    'Adel', 'Adham', 'Adil', 'Adnan', 'Afif', 'Ahsan', 'Aiman', 'Akeem', 'Akil', 'Alaa',
    'Aladdin', 'Alam', 'Alim', 'Aly', 'Ameen', 'Amir', 'Anas', 'Anwar', 'Aqil', 'Arif',
    'Arkan', 'Asad', 'Ashraf', 'Asif', 'Asim', 'Ayman', 'Azhar', 'Aziz', 'Badr', 'Baha',
    'Bakr', 'Bashir', 'Basim', 'Bilal', 'Burhan', 'Dawud', 'Dhia', 'Dhiya', 'Ehab', 'Emad',
    'Fadil', 'Fahd', 'Fahim', 'Faisal', 'Fajr', 'Fakhr', 'Farhan', 'Faris', 'Faruq', 'Fathi',
    'Fawaz', 'Fayez', 'Firas', 'Fouad', 'Ghalib', 'Ghassan', 'Habib', 'Hadi', 'Haitham', 'Hakim',
    'Hamdan', 'Hamid', 'Hani', 'Harith', 'Hasan', 'Hashim', 'Haytham', 'Hazem', 'Hilal', 'Hisham',
    'Husam', 'Ibrahim', 'Idris', 'Ihab', 'Ihsan', 'Ikram', 'Imad', 'Imran', 'Isam', 'Ismail',
    'Issam', 'Jabir', 'Jalal', 'Jamal', 'Jamil', 'Jasim', 'Jawad', 'Kadir', 'Kamal', 'Kareem',
    'Khaled', 'Khalil', 'Khattab', 'Labib', 'Latif', 'Luqman', 'Mahdi', 'Mahmood', 'Majid', 'Mansoor',
    'Marwan', 'Masoud', 'Mazhar', 'Mazin', 'Midhat', 'Moin', 'Mubarak', 'Mufid', 'Muhannad', 'Muhsin',
    'Mujahid', 'Munir', 'Murtaza', 'Mustafa', 'Nabeel', 'Nadeem', 'Naeem', 'Naji', 'Naseem', 'Nasir',
    'Nasser', 'Nawaf', 'Nazir', 'Nizar', 'Omar', 'Osama', 'Othman', 'Qadir', 'Qasim', 'Qays',
    'Rabee', 'Rafik', 'Rahim', 'Rami', 'Rashad', 'Rashid', 'Rayyan', 'Ridha', 'Ridwan', 'Sabir',
    'Sadiq', 'Saeed', 'Safi', 'Sajid', 'Salem', 'Salim', 'Salman', 'Sameer', 'Samir', 'Sami',
    'Shadi', 'Shafik', 'Shakir', 'Shams', 'Sharif', 'Shawki', 'Shoaib', 'Sohail', 'Sulaiman', 'Sultan',
    'Taha', 'Tariq', 'Tawfiq', 'Usama', 'Waleed', 'Wasim', 'Yahya', 'Yasir', 'Younis', 'Yusuf',
    'Zafar', 'Zahid', 'Zain', 'Zaki', 'Zayd', 'Ziad', 'Ziyad', 'Zubair', 'Zuhair', 'Zuleika'
]

def random_date(start, end):
    return (start + timedelta(days=random.randint(0, (end - start).days))).strftime("%Y-%m-%d")

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Truncate customers, bills, bill_items, employees
    cur.execute("DELETE FROM bill_items")
    cur.execute("DELETE FROM bills")
    cur.execute("DELETE FROM customers")
    cur.execute("DELETE FROM employees")
    conn.commit()

    # Add 10 realistic employees
    EMPLOYEES = [
        ("Ahmed Khalid", "0501234567", "Dubai, Al Barsha"),
        ("Fatima Noor", "0502345678", "Dubai, Deira"),
        ("Omar Hassan", "0503456789", "Sharjah, Al Majaz"),
        ("Layla Yasin", "0504567890", "Abu Dhabi, Al Khalidiya"),
        ("Samiya Rami", "0505678901", "Dubai, JLT"),
        ("Yusuf Imran", "0506789012", "Ajman, Al Nuaimia"),
        ("Huda Nasser", "0507890123", "Dubai, Business Bay"),
        ("Bilal Tariq", "0508901234", "Dubai, Al Quoz"),
        ("Rania Salim", "0509012345", "Sharjah, Al Nahda"),
        ("Majid Sultan", "0500123456", "Dubai, Marina")
    ]
    employee_ids = []
    for name, mobile, address in EMPLOYEES:
        cur.execute("INSERT INTO employees (name, mobile, address) VALUES (?, ?, ?)", (name, mobile, address))
        employee_ids.append(cur.lastrowid)
    conn.commit()

    # 2. Remove creation/insertion of cities and city_area tables (handled in schema)

    # 3. Fetch all cities and their areas
    cities = cur.execute("SELECT city_id, city_name FROM cities").fetchall()
    city_areas = {}
    for city in cities:
        city_areas[city['city_id']] = cur.execute("SELECT area_name FROM city_area WHERE city_id = ?", (city['city_id'],)).fetchall()

    # 4. Generate 700 customers, 65% from Dubai
    customers = []
    for i in range(700):
        # 65% Dubai, 35% other cities
        if random.random() < 0.65:
            city = next(c for c in cities if c['city_name'] == 'Dubai')
        else:
            city = random.choice([c for c in cities if c['city_name'] != 'Dubai'])
        areas = city_areas[city['city_id']]
        if not areas:
            area_name = ''
        else:
            area_name = random.choice(areas)['area_name']
        name = random.choice(MUSLIM_NAMES) + ' ' + random.choice(MUSLIM_NAMES)
        phone = f"05{random.randint(10000000,99999999)}"
        cur.execute("INSERT INTO customers (name, phone, city, area) VALUES (?, ?, ?, ?)", (name, phone, city['city_name'], area_name))
        customers.append(cur.lastrowid)
    conn.commit()

    # 5. Generate 2000 invoices using random customers and their city_area
    today = datetime.today()
    start_date = today - timedelta(days=180)
    products = cur.execute("SELECT product_id, product_name, rate FROM products").fetchall()
    bill_seq_by_date = {}
    for i in range(2000):
        bill_date = random_date(start_date, today)
        delivery_date = (datetime.strptime(bill_date, "%Y-%m-%d") + timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")
        cust_id = random.choice(customers)
        cust = cur.execute("SELECT * FROM customers WHERE customer_id = ?", (cust_id,)).fetchone()
        payment_method = random.choice(["Cash", "Card", "UPI"])
        # Generate Bill # in format BILL-YYYYMMDD-XXX
        bill_date_compact = bill_date.replace('-', '')
        seq = bill_seq_by_date.get(bill_date_compact, 0) + 1
        bill_seq_by_date[bill_date_compact] = seq
        bill_number = f"BILL-{bill_date_compact}-{seq:03d}"
        # Assign random master (employee)
        master_id = random.choice(employee_ids)
        # Select 1-5 random products
        items = random.sample(products, min(random.randint(1, 5), len(products)))
        subtotal = 0
        bill_items = []
        for prod in items:
            qty = random.randint(1, 3)
            rate = float(prod["rate"])
            discount = round(random.uniform(0, rate * 0.2), 2)
            adv = round(random.uniform(0, rate * 0.1), 2)
            total = qty * rate - discount - adv
            subtotal += total
            bill_items.append({
                "product_id": prod["product_id"],
                "product_name": prod["product_name"],
                "quantity": qty,
                "rate": rate,
                "discount": discount,
                "advance_paid": adv,
                "total_amount": total
            })
        vat_pct = 5.0
        vat_amount = round(subtotal * vat_pct / 100, 2)
        total_amount = round(subtotal + vat_amount, 2)
        advance_paid = 0
        balance_amount = total_amount
        cur.execute("""
            INSERT INTO bills (
                bill_number, customer_id, customer_name, customer_phone, customer_city, customer_area,
                bill_date, delivery_date, payment_method, subtotal, vat_amount, total_amount, advance_paid, balance_amount, master_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bill_number, cust["customer_id"], cust["name"], cust["phone"], cust["city"], cust["area"],
            bill_date, delivery_date, payment_method, subtotal, vat_amount, total_amount, advance_paid, balance_amount, master_id
        ))
        bill_id = cur.lastrowid
        for item in bill_items:
            cur.execute("""
                INSERT INTO bill_items (
                    bill_id, product_id, product_name, quantity, rate, discount, advance_paid, total_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bill_id, item["product_id"], item["product_name"], item["quantity"], item["rate"],
                item["discount"], item["advance_paid"], item["total_amount"]
            ))
        if (i+1) % 100 == 0:
            print(f"Inserted {i+1} invoices...")
            conn.commit()
    conn.commit()
    conn.close()
    print("Done! 700 customers and 2000 dummy invoices generated.")

if __name__ == "__main__":
    main() 