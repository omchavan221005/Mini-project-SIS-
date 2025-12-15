"""
Database initialization script for Store Inventory System
This script will create all tables and add sample data if needed
"""

from app import app, db, User, Product, Student, ProductAssignment
from datetime import datetime, timedelta
import random

def init_database():
    """Initialize the database with tables and sample data"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("[OK] Database tables created successfully!")
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("[OK] Created admin user (username: admin, password: admin)")
        else:
            print("[OK] Admin user already exists")
        
        # Check if we need sample data
        if Product.query.count() == 0:
            print("\nAdding sample products...")
            sample_products = [
                {
                    'name': 'Laptop Dell XPS 15',
                    'category': 'Electronics',
                    'quantity': 10,
                    'min_stock_level': 3,
                    'description': 'High-performance laptop for students'
                },
                {
                    'name': 'HP Printer LaserJet',
                    'category': 'Electronics',
                    'quantity': 5,
                    'min_stock_level': 2,
                    'description': 'Office printer'
                },
                {
                    'name': 'Whiteboard Markers',
                    'category': 'Stationery',
                    'quantity': 50,
                    'min_stock_level': 10,
                    'description': 'Assorted colors'
                },
                {
                    'name': 'Office Chair',
                    'category': 'Furniture',
                    'quantity': 15,
                    'min_stock_level': 5,
                    'description': 'Ergonomic office chair'
                },
                {
                    'name': 'Microscope',
                    'category': 'Lab Equipment',
                    'quantity': 8,
                    'min_stock_level': 2,
                    'description': 'Digital microscope for lab use'
                },
                {
                    'name': 'Basketball',
                    'category': 'Sports',
                    'quantity': 20,
                    'min_stock_level': 5,
                    'description': 'Official size basketball'
                },
                {
                    'name': 'Projector',
                    'category': 'Electronics',
                    'quantity': 4,
                    'min_stock_level': 1,
                    'description': 'HD projector for presentations'
                },
                {
                    'name': 'Notebooks A4',
                    'category': 'Stationery',
                    'quantity': 100,
                    'min_stock_level': 20,
                    'description': '200-page ruled notebooks'
                },
                {
                    'name': 'Study Desk',
                    'category': 'Furniture',
                    'quantity': 12,
                    'min_stock_level': 3,
                    'description': 'Wooden study desk'
                },
                {
                    'name': 'Calculator Scientific',
                    'category': 'Electronics',
                    'quantity': 2,
                    'min_stock_level': 5,
                    'description': 'Casio scientific calculator - LOW STOCK!'
                }
            ]
            
            for product_data in sample_products:
                product = Product(
                    name=product_data['name'],
                    category=product_data['category'],
                    quantity=product_data['quantity'],
                    min_stock_level=product_data['min_stock_level'],
                    description=product_data['description'],
                    date_of_issue=datetime.utcnow().date(),
                    is_assigned=False
                )
                db.session.add(product)
            
            db.session.commit()
            print(f"[OK] Added {len(sample_products)} sample products")
        
        # Check if we need sample students
        if Student.query.count() == 0:
            print("\nAdding sample students...")
            sample_students = [
                {
                    'full_name': 'John Doe',
                    'roll_number': 'CS2021001',
                    'email': 'john.doe@university.edu',
                    'phone': '+1234567890',
                    'department': 'Computer Science'
                },
                {
                    'full_name': 'Jane Smith',
                    'roll_number': 'EE2021002',
                    'email': 'jane.smith@university.edu',
                    'phone': '+1234567891',
                    'department': 'Electrical Engineering'
                },
                {
                    'full_name': 'Mike Johnson',
                    'roll_number': 'ME2021003',
                    'email': 'mike.johnson@university.edu',
                    'phone': '+1234567892',
                    'department': 'Mechanical Engineering'
                },
                {
                    'full_name': 'Sarah Williams',
                    'roll_number': 'CS2021004',
                    'email': 'sarah.williams@university.edu',
                    'phone': '+1234567893',
                    'department': 'Computer Science'
                },
                {
                    'full_name': 'David Brown',
                    'roll_number': 'BIO2021005',
                    'email': 'david.brown@university.edu',
                    'phone': '+1234567894',
                    'department': 'Biology'
                }
            ]
            
            for student_data in sample_students:
                student = Student(
                    full_name=student_data['full_name'],
                    roll_number=student_data['roll_number'],
                    email=student_data['email'],
                    phone=student_data['phone'],
                    department=student_data['department']
                )
                db.session.add(student)
            
            db.session.commit()
            print(f"[OK] Added {len(sample_students)} sample students")
            
            # Create some sample assignments
            print("\nCreating sample assignments...")
            students = Student.query.limit(3).all()
            products = Product.query.filter(Product.quantity > 0).limit(3).all()
            
            for i, (student, product) in enumerate(zip(students, products)):
                # Decrease product quantity
                product.quantity -= 1
                if product.quantity == 0:
                    product.is_assigned = True
                
                # Create assignment
                assignment = ProductAssignment(
                    product_id=product.id,
                    student_id=student.id,
                    assigned_date=datetime.utcnow() - timedelta(days=random.randint(1, 20)),
                    status='assigned'
                )
                db.session.add(assignment)
                
                # Update student record
                student.product_id = product.id
                student.assignment_date = assignment.assigned_date.date()
            
            db.session.commit()
            print(f"[OK] Created {len(students)} sample assignments")
        
        print("\n" + "="*50)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("="*50)
        print("\nYou can now login with:")
        print("  Username: admin")
        print("  Password: admin")
        print("\nRun the application with: python app.py")
        print("="*50)

if __name__ == '__main__':
    init_database()
