import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get('DATABASE_URL')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://', 'postgresql://', 1)

engine = create_engine(db_url)
with engine.connect() as conn:
    print("Checking/Adding due_date column to product_assignments...")
    try:
        conn.execute(text('ALTER TABLE product_assignments ADD COLUMN IF NOT EXISTS due_date TIMESTAMP'))
        conn.commit()
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
