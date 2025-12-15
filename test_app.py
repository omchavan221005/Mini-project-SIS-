"""
Quick test script to verify the application is working
"""

from app import app, db, Student, Product, ProductAssignment
from datetime import datetime

def test_app():
    with app.app_context():
        print("Testing Store Inventory System...")
        print("="*50)
        
        # Test 1: Check database connection
        try:
            student_count = Student.query.count()
            product_count = Product.query.count()
            assignment_count = ProductAssignment.query.count()
            
            print(f"[OK] Database connected successfully!")
            print(f"  - Students: {student_count}")
            print(f"  - Products: {product_count}")
            print(f"  - Assignments: {assignment_count}")
        except Exception as e:
            print(f"[ERROR] Database error: {e}")
            return False
        
        # Test 2: Check relationships
        try:
            students_with_products = Student.query.filter(Student.product_id.isnot(None)).all()
            print(f"\n[OK] Students with assigned products: {len(students_with_products)}")
            
            for student in students_with_products[:3]:  # Show first 3
                if student.current_product:
                    print(f"  - {student.full_name} has {student.current_product.name}")
        except Exception as e:
            print(f"[ERROR] Relationship error: {e}")
        
        # Test 3: Check active assignments
        try:
            active_assignments = ProductAssignment.query.filter_by(status='assigned').all()
            print(f"\n[OK] Active assignments: {len(active_assignments)}")
            
            for assignment in active_assignments[:3]:  # Show first 3
                if assignment.student and assignment.product:
                    print(f"  - {assignment.student.full_name} -> {assignment.product.name}")
        except Exception as e:
            print(f"[ERROR] Assignment error: {e}")
        
        print("\n" + "="*50)
        print("All tests completed!")
        print("\nYou can now run the application with: python app.py")
        print("Or use the start.bat file")
        return True

if __name__ == '__main__':
    test_app()
