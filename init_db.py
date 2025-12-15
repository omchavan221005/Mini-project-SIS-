from app import app, db, User, Product, Student, ProductAssignment, ActivityLog
from datetime import datetime, timedelta

def init_db():
    with app.app_context():
        # Create all database tables
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                is_admin=True,
                created_at=datetime.utcnow()
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            print('Created admin user with username: admin, password: admin123')
        
        # Create some sample data for testing
        if Product.query.count() == 0:
            # Add sample products
            products = [
                Product(
                    name='Laptop',
                    category='Electronics',
                    quantity=10,
                    min_stock_level=2,
                    description='Dell XPS 15',
                    date_of_issue=datetime.utcnow().date(),
                    is_assigned=False
                ),
                Product(
                    name='Textbook: Python Programming',
                    category='Stationery',
                    quantity=25,
                    min_stock_level=5,
                    description='Python Programming for Beginners',
                    date_of_issue=datetime.utcnow().date(),
                    is_assigned=False
                ),
                Product(
                    name='Lab Coat',
                    category='Lab Equipment',
                    quantity=15,
                    min_stock_level=3,
                    description='White lab coat, size M',
                    date_of_issue=datetime.utcnow().date(),
                    is_assigned=False
                )
            ]
            
            for product in products:
                db.session.add(product)
            
            # Add sample student
            student = Student(
                full_name='John Doe',
                roll_number='S001',
                email='john.doe@example.com',
                phone='1234567890',
                department='Computer Science',
                created_at=datetime.utcnow()
            )
            db.session.add(student)
            
            db.session.commit()
            print('Added sample data to the database.')
        
        print('Database initialization completed successfully!')

if __name__ == '__main__':
    init_db()
