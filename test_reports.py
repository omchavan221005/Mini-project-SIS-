"""
Test the reports page functionality
"""

from app import app, db, Product, Student, ProductAssignment

def test_reports_page():
    """Test that reports page loads with all data"""
    with app.test_client() as client:
        with app.app_context():
            # Login first
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['username'] = 'admin'
                sess['is_admin'] = True
            
            print("Testing Reports Page...")
            print("="*60)
            
            # Test reports page
            response = client.get('/reports')
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                print("[OK] Reports page loaded successfully!")
                
                # Check if page contains expected elements
                html = response.data.decode('utf-8')
                
                checks = [
                    ('Total Products', 'Total Products' in html),
                    ('Total Students', 'Total Students' in html),
                    ('Assigned Products', 'Assigned Products' in html),
                    ('Low Stock Alerts', 'Low Stock' in html),
                    ('Category Chart', 'categoryChart' in html),
                    ('Department Chart', 'departmentChart' in html),
                    ('Export Buttons', 'Export Products' in html and 'Export Students' in html),
                ]
                
                print("\nPage Content Checks:")
                all_passed = True
                for check_name, result in checks:
                    status = "[OK]" if result else "[FAIL]"
                    print(f"  {status} {check_name}")
                    if not result:
                        all_passed = False
                
                return all_passed
            else:
                print(f"[FAIL] Reports page failed to load: {response.status_code}")
                return False

def test_analytics_api():
    """Test the analytics API endpoint"""
    with app.test_client() as client:
        with app.app_context():
            # Login first
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['username'] = 'admin'
                sess['is_admin'] = True
            
            print("\nTesting Analytics API...")
            print("="*60)
            
            response = client.get('/api/analytics')
            
            if response.status_code == 200:
                data = response.get_json()
                if 'stock_trend' in data:
                    print(f"[OK] Analytics API working!")
                    print(f"  - Stock trend data points: {len(data['stock_trend'])}")
                    return True
                else:
                    print("[FAIL] Analytics API missing stock_trend data")
                    return False
            else:
                print(f"[FAIL] Analytics API failed: {response.status_code}")
                return False

def test_export_routes():
    """Test export functionality"""
    with app.test_client() as client:
        with app.app_context():
            # Login first
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['username'] = 'admin'
                sess['is_admin'] = True
            
            print("\nTesting Export Routes...")
            print("="*60)
            
            # Test products export
            response1 = client.get('/export/products')
            products_ok = response1.status_code == 200 and 'text/csv' in response1.headers.get('Content-Type', '')
            
            print(f"{'[OK]' if products_ok else '[FAIL]'} Export Products")
            
            # Test students export
            response2 = client.get('/export/students')
            students_ok = response2.status_code == 200 and 'text/csv' in response2.headers.get('Content-Type', '')
            
            print(f"{'[OK]' if students_ok else '[FAIL]'} Export Students")
            
            return products_ok and students_ok

if __name__ == '__main__':
    print("\n" + "="*60)
    print("REPORTS PAGE TESTING")
    print("="*60 + "\n")
    
    result1 = test_reports_page()
    result2 = test_analytics_api()
    result3 = test_export_routes()
    
    print("\n" + "="*60)
    if result1 and result2 and result3:
        print("ALL TESTS PASSED!")
        print("Reports page is fully functional!")
    else:
        print("SOME TESTS FAILED")
        print("Check the output above for details")
    print("="*60)
