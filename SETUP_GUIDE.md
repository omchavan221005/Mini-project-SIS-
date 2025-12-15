# Store Inventory Management System - Setup Guide

## Overview
A comprehensive Flask-based web application for managing store inventory with automatic stock tracking when items are assigned to students.

## New Features Added

### 1. Store Management Module
- **Inventory Dashboard**: View all products with real-time stock levels
- **Stock Tracking**: Automatic quantity updates when products are assigned/returned
- **Low Stock Alerts**: Visual warnings when items reach minimum stock levels
- **Product Categories**: Organize items by Electronics, Stationery, Furniture, Lab Equipment, Sports, and Other
- **Minimum Stock Levels**: Set thresholds for each product to trigger low stock alerts

### 2. Enhanced Product Model
- `quantity`: Current stock count
- `min_stock_level`: Threshold for low stock alerts
- `category`: Product categorization
- `description`: Detailed product information
- `is_low_stock`: Property that automatically checks if quantity ≤ min_stock_level
- `date_of_issue`: Date when product was added to inventory

### 3. Product Assignment Tracking
- **ProductAssignment Model**: Complete history of all product assignments
  - Tracks which student received which product
  - Records assignment and return dates
  - Maintains status (assigned/returned)
  - Allows notes for each transaction
- **Automatic Stock Updates**:
  - When a product is assigned: quantity decreases by 1
  - When a product is returned: quantity increases by 1
  - Products marked as "assigned" when quantity reaches 0

### 4. Student Management Enhancements
- View complete assignment history for each student
- Track current product assignments
- See all past assignments with dates

## Installation & Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Initialize Database
```bash
python init_db.py
```

This will:
- Create all necessary database tables
- Create an admin user (username: admin, password: admin123)
- Add sample products for testing

### Step 3: Run the Application
```bash
python app.py
```

The application will start on http://localhost:5000

## Default Login Credentials
- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change the default password after first login in production!

## Application Structure

```
Mini project(SIS)/
├── app.py                      # Main application with routes and models
├── init_db.py                  # Database initialization script
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
├── SETUP_GUIDE.md             # This file
├── instance/
│   └── inventory.db           # SQLite database (created after init)
├── logs/
│   └── inventory.log          # Application logs
├── uploads/                    # File uploads directory
└── templates/
    ├── login.html             # Login page
    ├── store.html             # Store management (NEW)
    ├── index.html             # Dashboard
    ├── student_details.html   # Student management
    ├── reports.html           # Reports
    ├── notifications.html     # Notifications
    └── settings.html          # Settings

## Key Features

### Store Management Page (`/store`)
1. **Inventory Summary Cards**:
   - Total Items: Sum of all product quantities
   - Low Stock Items: Count of products below minimum stock level
   - Assigned Items: Count of products currently assigned to students

2. **Product Table**:
   - Item Name
   - Category
   - In Stock (current quantity)
   - Minimum Stock Level
   - Status (Low Stock/In Stock badge)
   - Last Updated date
   - Edit action button

3. **Add/Edit Product Modal**:
   - Item Name (required)
   - Category dropdown (required)
   - Quantity (required, min: 0)
   - Minimum Stock Level (required, min: 1)
   - Description (optional)

### Automatic Stock Management
When you assign a product to a student:
1. Product quantity automatically decreases by 1
2. ProductAssignment record is created
3. Student's current assignment is updated
4. Activity is logged

When a student returns a product:
1. Product quantity automatically increases by 1
2. ProductAssignment status is updated to "returned"
3. Return date is recorded
4. Activity is logged

## API Endpoints

### Store Management
- `GET /store` - View store inventory
- `POST /add_product` - Add new product
- `POST /update_product` - Update existing product
- `POST /delete_product/<id>` - Delete product (admin only)

### Student & Assignment Management
- `GET /students` - View all students
- `POST /add_student` - Add new student
- `POST /assign_product/<student_id>` - Assign product to student
- `POST /return_product/<student_id>` - Return product from student

### Authentication
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /logout` - Logout

## Database Models

### User
- username, password_hash, is_admin, last_login, created_at

### Product
- name, description, quantity, min_stock_level, category
- date_of_issue, is_assigned, created_at
- Property: `is_low_stock` (returns True if quantity ≤ min_stock_level)

### Student
- full_name, roll_number, email, phone, department
- product_id (current assignment), assignment_date, return_date
- created_at, updated_at

### ProductAssignment
- product_id, student_id, assigned_date, returned_date
- status (assigned/returned), notes, created_at

### ActivityLog
- user_id, action, details, timestamp, ip_address

## Usage Examples

### Adding a New Product
1. Navigate to Store Management (`/store`)
2. Click "Add New Item" button
3. Fill in the form:
   - Name: "Laptop Dell XPS 15"
   - Category: "Electronics"
   - Quantity: 10
   - Min Stock Level: 2
4. Click "Save Changes"

### Assigning a Product to a Student
1. Navigate to Students page (`/students`)
2. Find the student
3. Click "Assign Product"
4. Select product from dropdown
5. Confirm assignment
6. Product quantity automatically decreases by 1

### Returning a Product
1. Navigate to Students page
2. Find student with assigned product
3. Click "Return Product"
4. Confirm return
5. Product quantity automatically increases by 1

## Security Features
- CSRF protection on all forms
- Session-based authentication
- Password hashing (Werkzeug)
- Login required decorators
- Admin-only routes for sensitive operations
- Activity logging for audit trail

## Troubleshooting

### Database Issues
If you encounter database errors:
```bash
# Delete old database
del instance\inventory.db

# Reinitialize
python init_db.py
```

### Import Errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Port Already in Use
If port 5000 is busy, modify `app.py`:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change port
```

## Next Steps
1. Change default admin password
2. Add your products to inventory
3. Add student records
4. Start assigning products
5. Monitor stock levels
6. Review activity logs regularly

## Support
For issues or questions, please check:
- README.md for general information
- Application logs in `logs/inventory.log`
- Flask documentation: https://flask.palletsprojects.com/

## License
MIT License - See LICENSE file for details
