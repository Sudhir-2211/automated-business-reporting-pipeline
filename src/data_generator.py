import os
import sqlite3
from datetime import datetime, timedelta
import random


def generate_synthetic_business_db(db_path: str = "data/business_warehouse.db"):
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS order_items;")
    cur.execute("DROP TABLE IF EXISTS orders;")
    cur.execute("DROP TABLE IF EXISTS products;")
    cur.execute("DROP TABLE IF EXISTS customers;")

    # 1. Customers Table
    cur.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        region TEXT NOT NULL,
        segment TEXT NOT NULL,
        signup_date DATE NOT NULL
    );
    """)

    # 2. Products Table
    cur.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit_price REAL NOT NULL,
        unit_cost REAL NOT NULL
    );
    """)

    # 3. Orders Table
    cur.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        order_date DATE NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    """)

    # 4. Order Items Table
    cur.execute("""
    CREATE TABLE order_items (
        item_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        discount REAL NOT NULL DEFAULT 0.0,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)

    # Seed Customers
    regions = ["North America", "Europe", "Asia Pacific", "Latin America"]
    segments = ["Enterprise", "Mid-Market", "SMB"]
    customers_data = []
    base_date = datetime(2025, 1, 1)

    for i in range(1, 51):
        signup = (base_date + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
        customers_data.append((
            i,
            f"Client-{i:03d}",
            random.choice(regions),
            random.choice(segments),
            signup,
        ))
    cur.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?);", customers_data)

    # Seed Products
    products_catalog = [
        (1, "Cloud Compute Instance (4 vCPU)", "Cloud Services", 120.0, 45.0),
        (2, "Managed PostgreSQL DB", "Cloud Services", 200.0, 75.0),
        (3, "Enterprise Security Suite", "Software", 350.0, 60.0),
        (4, "Dedicated Fiber Gateway", "Hardware", 450.0, 220.0),
        (5, "DevOps Architecture Consulting", "Professional Services", 150.0, 80.0),
        (6, "Backup & Disaster Recovery Plan", "Cloud Services", 80.0, 25.0),
    ]
    cur.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?);", products_catalog)

    # Seed Orders & Order Items
    orders_data = []
    items_data = []
    order_id = 1001
    item_id = 5001

    start_date = datetime(2026, 8, 1)
    for day_offset in range(60):  # 60 days of activity
        current_day = start_date + timedelta(days=day_offset)
        daily_order_count = random.randint(3, 8)

        # Anomaly simulation: day 45 had an unexpected revenue dip
        if day_offset == 45:
            daily_order_count = 1

        for _ in range(daily_order_count):
            cust_id = random.randint(1, 50)
            status = random.choices(["COMPLETED", "REFUNDED", "PENDING"], weights=[0.9, 0.05, 0.05])[0]
            orders_data.append((order_id, cust_id, current_day.strftime("%Y-%m-%d"), status))

            # 1 to 3 items per order
            for _ in range(random.randint(1, 3)):
                prod = random.choice(products_catalog)
                qty = random.randint(1, 5)
                disc = random.choice([0.0, 0.05, 0.10])
                items_data.append((item_id, order_id, prod[0], qty, disc))
                item_id += 1

            order_id += 1

    cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?);", orders_data)
    cur.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?);", items_data)

    conn.commit()
    conn.close()
    return db_path


if __name__ == "__main__":
    generate_synthetic_business_db()
    print("Synthetic database generated successfully.")
