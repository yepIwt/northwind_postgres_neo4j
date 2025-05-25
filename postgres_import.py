import psycopg2
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_NAME = os.getenv("DB_NAME", "northwind")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def safe_execute(cur, query, params=None):
    try:
        cur.execute(query, params or ())
    except Exception as e:
        print(f"❌ Error executing query:\n{query}\n" f"With params: {params}\n\n{e}")
        raise


def create_categories_table(cur):
    safe_execute(
        cur,
        """
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT NOT NULL,
            description TEXT,
            picture BYTEA
        );
    """,
    )


def import_categories_data(cur, path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            picture_bytes = (
                bytes.fromhex(row["picture"][2:])
                if row["picture"].startswith("0x")
                else None
            )
            safe_execute(
                cur,
                """
                INSERT INTO categories 
                (category_id, category_name, description, picture)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (category_id) DO NOTHING;
            """,
                (
                    int(row["categoryID"]),
                    row["categoryName"],
                    row["description"],
                    picture_bytes,
                ),
            )


def create_customers_table(cur):
    safe_execute(
        cur,
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            contact_name TEXT,
            contact_title TEXT,
            address TEXT,
            city TEXT,
            region TEXT,
            postal_code TEXT,
            country TEXT,
            phone TEXT,
            fax TEXT
        );
    """,
    )


def import_customers_data(cur, path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            safe_execute(
                cur,
                """
                INSERT INTO customers VALUES 
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (customer_id) DO NOTHING;
            """,
                tuple(row.values()),
            )


def create_employees_table(cur):
    safe_execute(
        cur,
        """
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            title TEXT,
            title_of_courtesy TEXT,
            birth_date DATE,
            hire_date DATE,
            address TEXT,
            city TEXT,
            region TEXT,
            postal_code TEXT,
            country TEXT,
            home_phone TEXT,
            extension TEXT,
            photo BYTEA,
            notes TEXT,
            reports_to INTEGER,
            photo_path TEXT
        );
    """,
    )


def import_employees_data(cur, path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            photo = (
                bytes.fromhex(row["photo"][2:])
                if row["photo"].startswith("0x")
                else None
            )
            reports_to = (
                int(row["reportsTo"])
                if (row["reportsTo"].strip().upper() != "NULL" and row["reportsTo"])
                else None
            )
            birth = datetime.strptime(row["birthDate"], "%Y-%m-%d %H:%M:%S.%f").date()
            hire = datetime.strptime(row["hireDate"], "%Y-%m-%d %H:%M:%S.%f").date()
            safe_execute(
                cur,
                """
                INSERT INTO employees VALUES 
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (employee_id) DO NOTHING;
            """,
                (
                    int(row["employeeID"]),
                    row["lastName"],
                    row["firstName"],
                    row["title"],
                    row["titleOfCourtesy"],
                    birth,
                    hire,
                    row["address"],
                    row["city"],
                    row["region"],
                    row["postalCode"],
                    row["country"],
                    row["homePhone"],
                    row["extension"],
                    photo,
                    row["notes"],
                    reports_to,
                    row["photoPath"],
                ),
            )


def create_orders_table(cur):
    safe_execute(
        cur,
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id TEXT REFERENCES customers(customer_id),
            employee_id INTEGER REFERENCES employees(employee_id),
            order_date DATE,
            required_date DATE,
            shipped_date DATE,
            ship_via INTEGER,
            freight NUMERIC,
            ship_name TEXT,
            ship_address TEXT,
            ship_city TEXT,
            ship_region TEXT,
            ship_postal_code TEXT,
            ship_country TEXT
        );
    """,
    )


def parse_date(date_str):
    """Parse date string or return None if NULL"""
    if date_str.strip().upper() == "NULL":
        return None
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f").date()


def import_orders_data(cur, path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            safe_execute(
                cur,
                """
                INSERT INTO orders VALUES 
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (order_id) DO NOTHING;
            """,
                (
                    int(row["orderID"]),
                    row["customerID"],
                    int(row["employeeID"]),
                    parse_date(row["orderDate"]),
                    parse_date(row["requiredDate"]),
                    parse_date(row["shippedDate"]),
                    int(row["shipVia"]),
                    float(row["freight"]),
                    row["shipName"],
                    row["shipAddress"],
                    row["shipCity"],
                    (
                        row["shipRegion"]
                        if row["shipRegion"].upper() != "NULL"
                        else None
                    ),
                    (
                        row["shipPostalCode"]
                        if row["shipPostalCode"].upper() != "NULL"
                        else None
                    ),
                    row["shipCountry"],
                ),
            )


def create_products_table(cur):
    safe_execute(
        cur,
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            supplier_id INTEGER,
            category_id INTEGER REFERENCES categories(category_id),
            quantity_per_unit TEXT,
            unit_price NUMERIC,
            units_in_stock INTEGER,
            units_on_order INTEGER,
            reorder_level INTEGER,
            discontinued BOOLEAN
        );
    """,
    )


def import_products_data(cur, path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            safe_execute(
                cur,
                """
                INSERT INTO products VALUES 
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (product_id) DO NOTHING;
            """,
                (
                    int(row["productID"]),
                    row["productName"],
                    int(row["supplierID"]),
                    int(row["categoryID"]),
                    row["quantityPerUnit"],
                    float(row["unitPrice"]),
                    int(row["unitsInStock"]),
                    int(row["unitsOnOrder"]),
                    int(row["reorderLevel"]),
                    row["discontinued"] == "1",
                ),
            )


def create_regions_table(cur):
    safe_execute(
        cur,
        """
        CREATE TABLE IF NOT EXISTS regions (
            region_id INTEGER PRIMARY KEY,
            region_description TEXT NOT NULL
        );
    """,
    )


def import_regions_data(cur, path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            safe_execute(
                cur,
                """
                INSERT INTO regions VALUES (%s, %s)
                ON CONFLICT (region_id) DO NOTHING;
            """,
                (int(row["regionID"]), row["regionDescription"]),
            )


def create_shippers_table(cur):
    safe_execute(
        cur,
        """
        CREATE TABLE IF NOT EXISTS shippers (
            shipper_id INTEGER PRIMARY KEY,
            company_name TEXT NOT NULL,
            phone TEXT
        );
    """,
    )


def import_shippers_data(cur, path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            safe_execute(
                cur,
                """
                INSERT INTO shippers VALUES (%s, %s, %s)
                ON CONFLICT (shipper_id) DO NOTHING;
            """,
                (int(row["shipperID"]), row["companyName"], row["phone"]),
            )


def create_suppliers_table(cur):
    safe_execute(
        cur,
        """
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INTEGER PRIMARY KEY,
            company_name TEXT NOT NULL,
            contact_name TEXT,
            contact_title TEXT,
            address TEXT,
            city TEXT,
            region TEXT,
            postal_code TEXT,
            country TEXT,
            phone TEXT,
            fax TEXT,
            home_page TEXT
        );
    """,
    )


def import_suppliers_data(cur, path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            safe_execute(
                cur,
                """
                INSERT INTO suppliers VALUES 
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (supplier_id) DO NOTHING;
            """,
                (
                    int(row["supplierID"]),
                    row["companyName"],
                    row["contactName"],
                    row["contactTitle"],
                    row["address"],
                    row["city"],
                    (
                        None
                        if row["region"].strip().upper() == "NULL"
                        else row["region"]
                    ),
                    row["postalCode"],
                    row["country"],
                    row["phone"],
                    (None if row["fax"].strip().upper() == "NULL" else row["fax"]),
                    (
                        None
                        if row["homePage"].strip().upper() == "NULL"
                        else row["homePage"]
                    ),
                ),
            )


def create_territories_table(cur):
    safe_execute(
        cur,
        """
        CREATE TABLE IF NOT EXISTS territories (
            territory_id TEXT PRIMARY KEY,
            territory_description TEXT NOT NULL,
            region_id INTEGER REFERENCES regions(region_id)
        );
    """,
    )


def import_territories_data(cur, path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            safe_execute(
                cur,
                """
                INSERT INTO territories VALUES (%s, %s, %s)
                ON CONFLICT (territory_id) DO NOTHING;
            """,
                (row["territoryID"], row["territoryDescription"], int(row["regionID"])),
            )


def create_employee_territories_table(cur):
    safe_execute(
        cur,
        """
        CREATE TABLE IF NOT EXISTS employee_territories (
            employee_id INTEGER REFERENCES employees(employee_id),
            territory_id TEXT REFERENCES territories(territory_id),
            PRIMARY KEY (employee_id, territory_id)
        );
    """,
    )


def import_employee_territories_data(cur, path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            safe_execute(
                cur,
                """
                INSERT INTO employee_territories VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
            """,
                (int(row["employeeID"]), row["territoryID"]),
            )


def create_order_details_table(cur):
    safe_execute(
        cur,
        """
        CREATE TABLE IF NOT EXISTS order_details (
            order_id INTEGER REFERENCES orders(order_id),
            product_id INTEGER REFERENCES products(product_id),
            unit_price NUMERIC NOT NULL,
            quantity INTEGER NOT NULL,
            discount NUMERIC NOT NULL,
            PRIMARY KEY (order_id, product_id)
        );
    """,
    )


def import_order_details_data(cur, path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            safe_execute(
                cur,
                """
                INSERT INTO order_details VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """,
                (
                    int(row["orderID"]),
                    int(row["productID"]),
                    float(row["unitPrice"]),
                    int(row["quantity"]),
                    float(row["discount"]),
                ),
            )


def main():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.autocommit = True
        cur = conn.cursor()

        print("🚧 Creating tables...")
        create_categories_table(cur)
        create_customers_table(cur)
        create_employees_table(cur)
        create_orders_table(cur)
        create_products_table(cur)
        create_regions_table(cur)
        create_shippers_table(cur)
        create_suppliers_table(cur)
        create_territories_table(cur)
        create_employee_territories_table(cur)
        create_order_details_table(cur)

        print("📦 Importing data...")
        import_categories_data(cur, "import/categories.csv")
        import_customers_data(cur, "import/customers.csv")
        import_employees_data(cur, "import/employees.csv")
        import_orders_data(cur, "import/orders.csv")
        import_products_data(cur, "import/products.csv")
        import_regions_data(cur, "import/regions.csv")
        import_shippers_data(cur, "import/shippers.csv")
        import_suppliers_data(cur, "import/suppliers.csv")
        import_territories_data(cur, "import/territories.csv")
        import_employee_territories_data(cur, "import/employee-territories.csv")
        import_order_details_data(cur, "import/order-details.csv")

        print("✅ Done.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"💥 FATAL ERROR: {e}")


if __name__ == "__main__":
    main()
