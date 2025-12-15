"""
Test script to verify form submissions work
"""

from app import app, db, Student, Product
from flask import session

def test_add_student():
    """Test adding a student via the route"""
    with app.test_client() as client:
        with app.app_context():
            # Login first
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['username'] = 'admin'
                sess['is_admin'] = True
            
            # Test data
            data = {
                'fullName': 'Test Student',
                'rollNumber': 'TEST001',
                'department': 'CSE',
                'email': 'test@example.com',
                'phone': '1234567890'
            }
            
            print("Testing student addition...")
            print(f"Data to send: {data}")
            
            # Send POST request
            response = client.post('/add_student', data=data, follow_redirects=True)
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data[:500]}")  # First 500 chars
            
            # Check if student was added
            student = Student.query.filter_by(roll_number='TEST001').first()
            if student:
                print(f"✓ SUCCESS! Student added: {student.full_name}")
                # Clean up
                db.session.delete(student)
                db.session.commit()
                return True
            else:
                print("✗ FAILED! Student not found in database")
                return False

def test_assign_product():
    """Test assigning a product to a student"""
    with app.test_client() as client:
        with app.app_context():
            # Login first
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['username'] = 'admin'
                sess['is_admin'] = True
            
            # Get first student and product
            student = Student.query.first()
            product = Product.query.filter(Product.quantity > 0).first()
            
            if not student or not product:
                print("✗ No student or product available for testing")
                return False
            
            print(f"\nTesting product assignment...")
            print(f"Student: {student.full_name} (ID: {student.id})")
            print(f"Product: {product.name} (ID: {product.id}, Qty: {product.quantity})")
            
            # Test data
            data = {
                'productId': str(product.id)
            }
            
            # Send POST request
            response = client.post(f'/assign_product/{student.id}', data=data, follow_redirects=True)
            
            print(f"Response status: {response.status_code}")
            
            # Refresh student from database
            db.session.refresh(student)
            
            if student.product_id == product.id:
                print(f"✓ SUCCESS! Product assigned to student")
                return True
            else:
                print(f"✗ FAILED! Product not assigned. Student product_id: {student.product_id}")
                return False

if __name__ == '__main__':
    print("="*60)
    print("FORM TESTING")
    print("="*60)
    
    result1 = test_add_student()
    result2 = test_assign_product()
    
    print("\n" + "="*60)
    if result1 and result2:
        print("ALL TESTS PASSED ✓")
    else:
        print("SOME TESTS FAILED ✗")
    print("="*60)
