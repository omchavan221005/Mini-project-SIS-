# Quick Start Guide - Store Inventory System

## Running the Application

### Option 1: Using the Batch File (Easiest)
Simply double-click `start.bat` in the project folder. This will:
- Start the Flask server
- Automatically open your browser to http://127.0.0.1:5000

### Option 2: Using Command Line
```bash
python app.py
```
Then open your browser and go to: http://127.0.0.1:5000

## Login Credentials
- **Username:** admin
- **Password:** admin

## Features Available

### 1. Dashboard (/)
- View inventory statistics
- See active assignments
- Monitor low stock items
- View products by category chart
- Quick action buttons

### 2. Store Management (/store)
- Add new products
- Edit existing products
- View all inventory items
- Track stock levels
- See low stock alerts

### 3. Student Management (/students)
- Add new students
- Assign products to students
- Return products from students
- View assignment history

### 4. Reports (/reports)
- View comprehensive statistics
- See recent assignments
- Track inventory trends

### 5. Notifications (/notifications)
- Low stock alerts
- Overdue assignment notifications

### 6. Settings (/settings)
- System configuration options

## Database Information
- **Database Type:** SQLite
- **Database Location:** `instance/inventory.db`
- **Initialization Script:** `init_database.py`

## Troubleshooting

### If the database needs to be reset:
```bash
python init_database.py
```

### If you get import errors:
```bash
pip install -r requirements.txt
```

### If port 5000 is already in use:
Edit `app.py` and change the port in the last line:
```python
app.run(debug=True, port=5001)  # Change to any available port
```

## Key Functionalities

### Adding a Product
1. Go to Store Management
2. Click "Add New Item"
3. Fill in the form (Name, Category, Quantity, Min Stock Level)
4. Click "Save Changes"

### Assigning a Product to a Student
1. Go to Students page
2. Find the student
3. Click "Assign Product"
4. Select the product from dropdown
5. Confirm assignment

### Returning a Product
1. Go to Students page
2. Find the student with assigned product
3. Click "Return Product"
4. Confirm return

## System Requirements
- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Edge)
- Windows/Linux/Mac OS

## Support
For issues or questions, check the main README.md file or review the code comments in app.py.
