"""
Uzum Market Relational Database Schema Specification
=====================================================
Ushbu modul relyatsion ma'lumotlar bazasi (SQLite / PostgreSQL) jadvallari,
birlamchi va tashqi kalitlar (PK/FK) hamda tezkor tahliliy so'rovlar uchun
indekslarni aniqlaydi.
"""

DDL_CATEGORIES = """
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT NOT NULL
);
"""

DDL_PRODUCTS = """
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    category_id INTEGER,
    price_current INTEGER NOT NULL,
    price_original INTEGER,
    discount_percentage REAL DEFAULT 0.0,
    monthly_installment INTEGER DEFAULT 0,
    has_installment BOOLEAN DEFAULT 0,
    rating REAL DEFAULT 0.0,
    reviews_count INTEGER DEFAULT 0,
    orders_count INTEGER DEFAULT 0,
    is_eco BOOLEAN DEFAULT 0,
    is_adult BOOLEAN DEFAULT 0,
    delivery_time_days INTEGER DEFAULT 1,
    delivery_type TEXT DEFAULT 'PVZ',
    crawled_at TEXT,
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
);
"""

DDL_CUSTOMERS = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    region TEXT NOT NULL,
    first_order_date TEXT,
    last_order_date TEXT,
    total_orders INTEGER DEFAULT 0,
    total_spent INTEGER DEFAULT 0
);
"""

DDL_ORDERS = """
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_date TEXT NOT NULL,
    region TEXT NOT NULL,
    delivery_type TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    status TEXT NOT NULL,
    items_count INTEGER NOT NULL,
    total_amount INTEGER NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);
"""

DDL_ORDER_ITEMS = """
CREATE TABLE IF NOT EXISTS order_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price INTEGER NOT NULL,
    line_total INTEGER NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_products_category ON products (category_id);",
    "CREATE INDEX IF NOT EXISTS idx_products_price ON products (price_current);",
    "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders (customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_orders_date ON orders (order_date);",
    "CREATE INDEX IF NOT EXISTS idx_orders_region ON orders (region);",
    "CREATE INDEX IF NOT EXISTS idx_orders_payment ON orders (payment_method);",
    "CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items (order_id);",
    "CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items (product_id);",
]

ALL_TABLES = [
    ("categories", DDL_CATEGORIES),
    ("products", DDL_PRODUCTS),
    ("customers", DDL_CUSTOMERS),
    ("orders", DDL_ORDERS),
    ("order_items", DDL_ORDER_ITEMS),
]
