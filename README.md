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
