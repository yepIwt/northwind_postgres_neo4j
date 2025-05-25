# Northwind for PostgreSQL and Neo4j

This project contains scripts to import the Northwind sample database into PostgreSQL and Neo4j.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

The PostgreSQL import script uses environment variables for database configuration. 

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and update the database connection parameters:
   ```
   DB_NAME=northwind
   DB_USER=postgres
   DB_PASSWORD=your_actual_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

### 3. Run PostgreSQL Import

Ensure your PostgreSQL server is running and the database exists, then run:

```bash
python postgres_import.py
```

The script will:
- Create all necessary tables
- Import data from CSV files
- Handle conflicts by skipping duplicate records

## Environment Variables

The following environment variables are used by `postgres_import.py`:

- `DB_NAME`: PostgreSQL database name (default: "northwind")
- `DB_USER`: PostgreSQL username (default: "postgres")
- `DB_PASSWORD`: PostgreSQL password (default: "your_password")
- `DB_HOST`: PostgreSQL host (default: "localhost") 
- `DB_PORT`: PostgreSQL port (default: "5432")

All variables have defaults, but it's recommended to set them explicitly in your `.env` file.


## Neo4j
Создать проект
![image](https://github.com/user-attachments/assets/966b19c2-ee5b-4e9f-a312-ff7f587035fa)

add - local dbms
![image](https://github.com/user-attachments/assets/ffc52408-7bcb-4247-9153-96675d719502)

любое название и пароль - create
![image](https://github.com/user-attachments/assets/26fc49ee-fc39-41eb-aca4-5b26cb0fa49d)

start
![image](https://github.com/user-attachments/assets/0866bec8-fae9-4720-870d-91dd7c27c938)

open
![image](https://github.com/user-attachments/assets/b24c6f9c-2628-4ab5-9689-72c214ab0aee)

запросы:
```cypher
LOAD CSV WITH HEADERS FROM "https://data.neo4j.com/northwind/products.csv" AS row
CREATE (n:Product)
SET n = row,
n.unitPrice = toFloat(row.unitPrice),
n.unitsInStock = toInteger(row.unitsInStock), n.unitsOnOrder = toInteger(row.unitsOnOrder),
n.reorderLevel = toInteger(row.reorderLevel), n.discontinued = (row.discontinued <> "0");

LOAD CSV WITH HEADERS FROM "https://data.neo4j.com/northwind/categories.csv" AS row
CREATE (n:Category)
SET n = row;

LOAD CSV WITH HEADERS FROM "https://data.neo4j.com/northwind/suppliers.csv" AS row
 CREATE (n:Supplier)
 SET n = row;

CREATE INDEX product_productID_index FOR (n:Product) ON (n.productID);
CREATE INDEX category_categoryID_index FOR (n:Category) ON (n.categoryID);
CREATE INDEX supplier_supplierID_index FOR (n:Supplier) ON (n.supplierID);

MATCH (p:Product),(c:Category)
WHERE p.categoryID = c.categoryID
CREATE (p)-[:PART_OF]->(c);

MATCH (p:Product),(s:Supplier)
WHERE p.supplierID = s.supplierID
CREATE (s)-[:SUPPLIES]->(p);

LOAD CSV WITH HEADERS FROM "https://data.neo4j.com/northwind/customers.csv" AS row
CREATE (n:Customer)
SET n = row;

LOAD CSV WITH HEADERS FROM "https://data.neo4j.com/northwind/orders.csv" AS row
CREATE (n:Order)
SET n = row;

CREATE INDEX customer_customerID_index FOR (n:Customer) ON (n.customerID);
CREATE INDEX order_orderID_index FOR (n:Order) ON (n.orderID);

MATCH (c:Customer),(o:Order)
WHERE c.customerID = o.customerID
CREATE (c)-[:PURCHASED]->(o);

LOAD CSV WITH HEADERS FROM "https://data.neo4j.com/northwind/order-details.csv" AS row
MATCH (p:Product), (o:Order)
WHERE p.productID = row.productID AND o.orderID = row.orderID
CREATE (o)-[details:ORDERS]->(p)
SET details = row, details.quantity = toInteger(row.quantity);
```


## Чек что одинаковые базы

```sql
SELECT p.product_name, c.category_name
FROM products p
JOIN categories c ON p.category_id = c.category_id
ORDER BY p.product_name
LIMIT 10;
```
![image](https://github.com/user-attachments/assets/2fc77e4f-f445-4087-8da5-488655e2b0d4)

```
MATCH (p:Product)-[:PART_OF]->(c:Category)
RETURN p.productName, c.categoryName
ORDER BY p.productName
LIMIT 10;
```
![image](https://github.com/user-attachments/assets/26d69566-5caa-4bd8-af5e-edf65553b2b1)


