import os
from sqlalchemy import text, create_engine
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get('DATABASE_URL')
if not db_url:
    print("DATABASE_URL not found in environment.")
    exit(1)

# PostgreSQL URL might need a fix for SQLAlchemy 2.0 (postgres:// -> postgresql://)
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

print(f"Connecting to database to sync sequences...")
engine = create_engine(db_url)

tables = ['users', 'products', 'activity_logs', 'students', 'product_assignments']

with engine.connect() as connection:
    for table in tables:
        try:
            print(f"Syncing sequence for table: {table}")
            max_id_query = text(f"SELECT COALESCE(MAX(id), 0) FROM {table}")
            max_id = connection.execute(max_id_query).scalar()
            
            print(f"Max ID in {table} is {max_id}. Setting sequence to {max_id + 1}...")
            
            sync_query = text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), :val, false)")
            connection.execute(sync_query, {"val": max_id + 1})
            
            connection.commit()
            print(f"Successfully synced sequence for {table}")
        except Exception as e:
            print(f"Error syncing {table}: {str(e)}")

print("Sequence sync complete!")
