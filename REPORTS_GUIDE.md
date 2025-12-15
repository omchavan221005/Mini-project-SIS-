# Reports Page - User Guide

## ✅ Reports Page is Now Fully Functional!

### Test Results:
```
[OK] Reports page loaded successfully!
[OK] Total Products
[OK] Total Students
[OK] Assigned Products
[OK] Low Stock Alerts
[OK] Category Chart
[OK] Department Chart
[OK] Export Buttons
[OK] Analytics API working!
[OK] Export Products
[OK] Export Students

ALL TESTS PASSED!
```

---

## 📊 Features Available

### 1. Statistics Dashboard

**Four Key Metrics:**
- **Total Products** - Total number of products in inventory
- **Total Students** - Total number of registered students
- **Assigned Products** - Number of products currently assigned to students
- **Low Stock Alerts** - Number of products below minimum stock level

### 2. Visual Charts

#### Products by Category (Doughnut Chart)
- Shows distribution of products across categories
- Interactive chart with hover details
- Color-coded for easy identification
- Categories include:
  - Electronics
  - Stationery
  - Furniture
  - Lab Equipment
  - Sports
  - Other

#### Students by Department (Bar Chart)
- Shows number of students in each department
- Vertical bar chart for easy comparison
- Departments include:
  - Computer Science Engineering (CSE)
  - Electronics & Communication (ECE)
  - Mechanical Engineering (ME)
  - Civil Engineering (CE)
  - Electrical Engineering (EE)

#### Stock Levels Trend (Line Chart)
- Shows stock level changes over the last 30 days
- Smooth line graph with trend visualization
- Helps identify stock patterns
- Real-time data from API

### 3. Export Functionality

**Export Products to CSV:**
- Click "Export Products" button
- Downloads: `products_export.csv`
- Contains:
  - ID
  - Name
  - Category
  - Quantity
  - Min Stock Level
  - Description
  - Date of Issue
  - Status (In Stock / Low Stock)

**Export Students to CSV:**
- Click "Export Students" button
- Downloads: `students_export.csv`
- Contains:
  - ID
  - Full Name
  - Roll Number
  - Email
  - Phone
  - Department
  - Assigned Product
  - Assignment Date

### 4. Recent Activity

- Shows count of product assignments in the last 30 days
- Quick overview of system usage
- Helps track activity trends

---

## 🚀 How to Use

### Accessing Reports Page

1. **Login to the system**
   - Username: `admin`
   - Password: `admin`

2. **Navigate to Reports**
   - Click "Reports" in the navigation bar
   - Or go directly to: `http://127.0.0.1:5000/reports`

### Viewing Statistics

1. **Top Statistics Cards**
   - Four cards at the top show key metrics
   - Numbers update in real-time based on database
   - Color-coded for easy identification:
     - Blue: Total Products
     - Green: Total Students
     - Cyan: Assigned Products
     - Yellow: Low Stock Alerts

2. **Interactive Charts**
   - **Hover** over chart sections to see details
   - **Click** legend items to show/hide data
   - Charts auto-resize based on screen size

### Exporting Data

1. **Export Products:**
   ```
   Click "Export Products" button
   → File downloads automatically
   → Open in Excel, Google Sheets, or any CSV viewer
   ```

2. **Export Students:**
   ```
   Click "Export Students" button
   → File downloads automatically
   → Contains all student information including assignments
   ```

3. **Using Exported Data:**
   - Open in Microsoft Excel
   - Import to Google Sheets
   - Use for reports and presentations
   - Analyze in data analysis tools

---

## 📈 Understanding the Charts

### Products by Category Chart

**What it shows:**
- Percentage distribution of products
- Which categories have most/least products
- Inventory diversity

**How to read:**
- Larger sections = more products in that category
- Hover to see exact count
- Use for inventory planning

**Example:**
```
Electronics: 40% (4 products)
Stationery: 30% (3 products)
Furniture: 20% (2 products)
Lab Equipment: 10% (1 product)
```

### Students by Department Chart

**What it shows:**
- Number of students per department
- Department-wise distribution
- Student enrollment patterns

**How to read:**
- Taller bars = more students
- Compare departments at a glance
- Useful for resource allocation

**Example:**
```
CSE: 5 students
ECE: 3 students
ME: 2 students
CE: 1 student
```

### Stock Levels Trend Chart

**What it shows:**
- Stock quantity over last 30 days
- Trend: increasing, decreasing, or stable
- Historical stock patterns

**How to read:**
- Upward trend = stock increasing
- Downward trend = stock decreasing
- Flat line = stable stock
- Use for forecasting needs

---

## 💡 Use Cases

### 1. Monthly Reporting
```
1. Go to Reports page
2. Take screenshot of statistics
3. Export products and students data
4. Create monthly report with charts and data
```

### 2. Inventory Planning
```
1. Check "Low Stock Alerts" number
2. View Products by Category chart
3. Identify which categories need restocking
4. Export products list for ordering
```

### 3. Student Analysis
```
1. View Students by Department chart
2. Check "Assigned Products" count
3. Export students data
4. Analyze assignment patterns
```

### 4. Trend Analysis
```
1. View Stock Levels Trend chart
2. Identify patterns (seasonal, usage-based)
3. Plan future inventory needs
4. Optimize stock levels
```

---

## 🔧 Technical Details

### API Endpoints

**Analytics API:**
```
GET /api/analytics
Returns: JSON with stock trend data
Used by: Stock Levels Trend chart
```

**Export Products:**
```
GET /export/products
Returns: CSV file
Filename: products_export.csv
```

**Export Students:**
```
GET /export/students
Returns: CSV file
Filename: students_export.csv
```

### Data Sources

- **Statistics:** Real-time from database
- **Charts:** Aggregated queries on Product and Student tables
- **Trend Data:** Calculated from ProductAssignment history
- **Exports:** Complete data dump from respective tables

### Chart Libraries

- **Chart.js** - For all visualizations
- **Responsive** - Auto-adjusts to screen size
- **Interactive** - Hover effects and legends
- **Customizable** - Colors and styles

---

## 🎨 Customization

### Changing Chart Colors

Edit `reports.html` line 212-214:
```javascript
backgroundColor: [
    '#FF6384', '#36A2EB', '#FFCE56', 
    '#4BC0C0', '#9966FF', '#FF9F40'
]
```

### Adjusting Time Range

Edit `app.py` in `/api/analytics` route:
```python
# Change 30 to desired number of days
for i in range(30, 0, -1):
```

### Adding More Export Fields

Edit `app.py` in `/export/products` or `/export/students`:
```python
# Add more fields to CSV header and data
output.write('ID,Name,NewField,...\n')
```

---

## ⚠️ Troubleshooting

### Charts Not Showing

**Problem:** Blank chart areas

**Solutions:**
1. Check browser console (F12) for errors
2. Ensure Chart.js is loading:
   ```html
   <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
   ```
3. Verify data is being passed:
   - Check `category_data` and `department_data` in template
4. Hard refresh: `Ctrl + F5`

### Export Not Working

**Problem:** CSV files not downloading

**Solutions:**
1. Check browser download settings
2. Disable popup blocker
3. Try different browser
4. Check server logs for errors

### Wrong Statistics

**Problem:** Numbers don't match actual data

**Solutions:**
1. Refresh the page
2. Check database directly:
   ```bash
   python -c "from app import *; app.app_context().push(); print(Product.query.count())"
   ```
3. Clear browser cache
4. Restart Flask server

### API Errors

**Problem:** Stock trend chart not loading

**Solutions:**
1. Check `/api/analytics` endpoint:
   - Go to `http://127.0.0.1:5000/api/analytics`
   - Should return JSON data
2. Check browser console for fetch errors
3. Verify you're logged in

---

## 📊 Sample Reports

### Weekly Inventory Report

```
Week of: [Date]

INVENTORY SUMMARY
- Total Products: 10
- Total Stock: 150 units
- Low Stock Items: 2
- Assigned Products: 5

TOP CATEGORIES
1. Electronics: 40%
2. Stationery: 30%
3. Furniture: 20%
4. Lab Equipment: 10%

STUDENT DISTRIBUTION
- CSE: 5 students
- ECE: 3 students
- ME: 2 students

RECOMMENDATIONS
- Restock: Calculators (2 units)
- Review: High assignment rate in CSE
```

---

## 🎯 Best Practices

1. **Regular Monitoring**
   - Check reports weekly
   - Track trends over time
   - Identify patterns early

2. **Export Regularly**
   - Backup data monthly
   - Keep historical records
   - Use for audits

3. **Act on Insights**
   - Restock low items promptly
   - Balance inventory across categories
   - Optimize based on trends

4. **Share Reports**
   - Export and share with management
   - Use charts in presentations
   - Make data-driven decisions

---

## 🚀 Quick Start Checklist

- [ ] Access reports page
- [ ] View all four statistics
- [ ] Check Products by Category chart
- [ ] Check Students by Department chart
- [ ] View Stock Levels Trend
- [ ] Export products to CSV
- [ ] Export students to CSV
- [ ] Open exported files
- [ ] Verify data accuracy

---

**The Reports page is now fully functional with all features working!** 📊✨

For questions or issues, refer to the troubleshooting section above.
