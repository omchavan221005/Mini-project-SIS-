from app import db
from models import Product

def upgrade():
    # Add new columns to Product model
    db.engine.execute('''
        ALTER TABLE product 
        ADD COLUMN min_stock_level INTEGER NOT NULL DEFAULT 5,
        ADD COLUMN is_low_stock BOOLEAN NOT NULL DEFAULT FALSE,
        ADD COLUMN category VARCHAR(50),
        ADD COLUMN date_of_issue DATE
    ''')
    
    # Set default values for existing products
    db.engine.execute('''
        UPDATE product 
        SET 
            min_stock_level = 5,
            is_low_stock = (quantity <= 5),
            category = 'Other',
            date_of_issue = CURRENT_DATE
    ''')
    
    db.session.commit()

def downgrade():
    # Remove the added columns
    db.engine.execute('''
        ALTER TABLE product 
        DROP COLUMN min_stock_level,
        DROP COLUMN is_low_stock,
        DROP COLUMN category,
        DROP COLUMN date_of_issue
    ''')
    db.session.commit()

if __name__ == '__main__':
    upgrade()
