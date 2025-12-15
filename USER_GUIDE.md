# Store Inventory System - User Guide

## 🚀 Quick Start

### Starting the Application

**Option 1: Double-click the batch file**
```
start.bat
```
This will automatically open your browser to http://127.0.0.1:5000

**Option 2: Command line**
```bash
python app.py
```
Then manually open: http://127.0.0.1:5000

### Login
- **Username:** `admin`
- **Password:** `admin`

---

## 📋 Features Overview

### 1. Dashboard (Home Page)
**URL:** `/` or `http://127.0.0.1:5000/`

**What you'll see:**
- **Statistics Cards:**
  - Total Products
  - Total Items in Stock
  - Active Assignments
  - Low Stock Items

- **Products by Category Chart:**
  - Visual pie chart showing product distribution

- **Recent Assignments Table:**
  - Last 5 product assignments
  - Student names and roll numbers
  - Product names and categories
  - Assignment dates
  - Status (Active/Returned)

- **Student Product Assignments:**
  - Complete list of all active assignments
  - Student details (Name, Roll Number, Department)
  - Assigned product information
  - Assignment dates

- **Low Stock Alert:**
  - Products below minimum stock level
  - Quick restock button

- **Quick Actions:**
  - Manage Inventory
  - Manage Students
  - View Reports
  - Notifications

---

## 👥 Student Management

### Adding a New Student

1. Click **"Students"** in the navigation bar
2. Fill in the form:
   - **Full Name** (Required)
   - **Roll Number** (Required, must be unique)
   - **Department** (Required) - Select from dropdown:
     - Computer Science Engineering (CSE)
     - Electronics & Communication (ECE)
     - Mechanical Engineering (ME)
     - Civil Engineering (CE)
     - Electrical Engineering (EE)
   - Email (Optional)
   - Phone (Optional)

3. Click **"Add Student"** button
4. ✅ Success message will appear if student is added
5. ❌ Error message will show if:
   - Required fields are missing
   - Roll number already exists

### Viewing Students

The student table shows:
- ID
- Full Name
- Roll Number
- Department
- Product Details (if assigned)
- Assignment Date
- Action buttons

### Assigning a Product to a Student

1. Find the student in the table
2. Click **"Assign Product"** button
3. A modal will open
4. Select a product from the dropdown
   - Shows product name and available quantity
5. Click **"Assign Product"**
6. ✅ Product is assigned and appears in the student row
7. Product quantity is automatically decreased by 1

**Note:** You can only assign products that have quantity > 0

### Returning a Product

1. Find the student with an assigned product
2. Click **"Return"** button
3. Confirm the action
4. ✅ Product is removed from student
5. Product quantity is automatically increased by 1

### Deleting a Student

1. Click **"Delete"** button next to the student
2. Confirm the deletion
3. ⚠️ Warning: This action cannot be undone

---

## 📦 Inventory Management

### Adding a New Product

1. Click **"Store Management"** in navigation
2. Click **"Add New Item"** button
3. Fill in the form:
   - **Item Name** (Required)
   - **Category** (Required) - Select from:
     - Electronics
     - Stationery
     - Furniture
     - Lab Equipment
     - Sports
     - Other
   - **Quantity** (Required, minimum 0)
   - **Minimum Stock Level** (Required, minimum 1)
   - **Description** (Optional)

4. Click **"Save Changes"**
5. ✅ Product is added to inventory

### Editing a Product

1. Find the product in the inventory table
2. Click **"Edit"** button
3. Modify the fields
4. Click **"Save Changes"**
5. ✅ Product is updated

### Deleting a Product

1. Click **"Delete"** button next to the product
2. Confirm the deletion
3. ⚠️ Cannot delete if product is currently assigned to students

### Low Stock Alerts

Products with quantity ≤ minimum stock level will:
- Show a **"Low Stock"** badge
- Appear in yellow/warning color
- Be listed in the Low Stock Alert section on dashboard

---

## 📊 Reports

**URL:** `/reports`

View comprehensive statistics:
- Total products in inventory
- Total students registered
- Active assignments count
- Low stock items count
- Recent assignment history (last 10)

---

## 🔔 Notifications

**URL:** `/notifications`

See important alerts:
- **Low Stock Products:**
  - Products below minimum stock level
  - Current quantity vs minimum required
  
- **Overdue Returns:**
  - Products assigned for more than 30 days
  - Student information
  - Days overdue

---

## ⚙️ Settings

**URL:** `/settings`

Configure system settings (future feature)

---

## 🔍 Search and Filter

### On Store Management Page:
- **Search Box:** Type to search products by name
- **Category Filter:** Filter products by category
- Real-time filtering as you type

### On Dashboard:
- View by status (Active/Returned)
- Sort by date
- Filter by student or product

---

## 💡 Tips and Best Practices

### For Students:
1. Always use unique roll numbers
2. Fill in department information for better tracking
3. Add email/phone for future notifications

### For Products:
1. Set realistic minimum stock levels
2. Use clear, descriptive product names
3. Categorize products correctly for better reporting
4. Update quantities regularly

### For Assignments:
1. Check product availability before assigning
2. Process returns promptly to maintain accurate inventory
3. Review dashboard regularly for overdue items

---

## ⚠️ Common Issues and Solutions

### Issue: Student not being added
**Solution:** 
- Check that all required fields are filled
- Ensure roll number is unique
- Look for error messages at the top of the page

### Issue: Cannot assign product
**Solution:**
- Verify product has quantity > 0
- Check if product is already assigned (for single items)
- Refresh the page and try again

### Issue: Product not showing in dropdown
**Solution:**
- Product must have quantity > 0
- Check Store Management to verify product exists
- Add more stock if needed

### Issue: Cannot delete product
**Solution:**
- Product cannot be deleted if assigned to students
- Return all assignments first
- Then delete the product

---

## 📱 Navigation Menu

| Menu Item | URL | Description |
|-----------|-----|-------------|
| Dashboard | `/` | Main overview page |
| Store Management | `/store` | Manage products |
| Students | `/students` | Manage students and assignments |
| Reports | `/reports` | View statistics and reports |
| Notifications | `/notifications` | See alerts and warnings |
| Settings | `/settings` | System configuration |
| Logout | `/logout` | End session |

---

## 🎯 Workflow Examples

### Example 1: New Student Gets a Laptop

1. Go to **Students** page
2. Add student:
   - Name: "John Doe"
   - Roll: "CS2024001"
   - Department: "CSE"
3. Click **"Assign Product"**
4. Select "Laptop Dell XPS 15"
5. Click **"Assign Product"**
6. ✅ John now has the laptop
7. View on Dashboard to confirm

### Example 2: Student Returns Equipment

1. Go to **Students** page
2. Find student with assigned product
3. Click **"Return"** button
4. Confirm return
5. ✅ Product is back in inventory
6. Check Store Management to see updated quantity

### Example 3: Restocking Low Items

1. Check **Dashboard** for Low Stock Alert
2. Note which products need restocking
3. Go to **Store Management**
4. Click **"Edit"** on low stock product
5. Increase quantity
6. Click **"Save Changes"**
7. ✅ Product no longer in low stock alert

---

## 🔐 Security Notes

- Change default admin password in production
- Keep database backups regularly
- Don't share login credentials
- Log out when finished

---

## 📞 Support

For issues or questions:
1. Check this user guide
2. Review FIXES_APPLIED.md for technical details
3. Check README.md for installation help
4. Review error messages carefully

---

## 🎓 Training Checklist

- [ ] Successfully logged in
- [ ] Added a new student
- [ ] Added a new product
- [ ] Assigned a product to a student
- [ ] Viewed assignment on dashboard
- [ ] Returned a product from a student
- [ ] Checked low stock alerts
- [ ] Used search and filter features
- [ ] Viewed reports
- [ ] Checked notifications

---

**Last Updated:** 2025-10-01
**Version:** 1.0
**System:** Store Inventory System (SIS)
