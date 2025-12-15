# Troubleshooting Guide

## ✅ GOOD NEWS: The Routes ARE Working!

### Test Results Show:
- `/add_student` route is receiving form data correctly
- Students ARE being added to the database
- Form data is being parsed properly

### Current Database Status:
```
Total students: 2
1: John Doe - S001
2: Test Student - TEST001
```

---

## Common Issues and Solutions

### Issue 1: "Student not appearing after adding"
**Cause:** Browser cache or page not refreshing

**Solutions:**
1. **Hard refresh the page:** Press `Ctrl + F5` or `Ctrl + Shift + R`
2. **Clear browser cache:**
   - Chrome: `Ctrl + Shift + Delete`
   - Firefox: `Ctrl + Shift + Delete`
3. **Try incognito/private mode**
4. **Restart the Flask server:**
   - Stop the current server (Ctrl + C)
   - Run `python app.py` again

### Issue 2: "Cannot assign products"
**Cause:** CSRF token or form submission issue

**Solutions:**
1. **Check browser console for errors:**
   - Press `F12` to open Developer Tools
   - Click "Console" tab
   - Look for red error messages

2. **Verify you're logged in:**
   - Check if you see "Logout" button in navbar
   - If not, go to `/login` and login again

3. **Make sure product has quantity > 0:**
   - Go to Store Management
   - Check the product quantity
   - If 0, edit and increase quantity

### Issue 3: "Form submits but nothing happens"
**Cause:** JavaScript preventing form submission or modal not closing

**Solutions:**
1. **Remove the form reset JavaScript** (temporary):
   - The JavaScript at the bottom of student_details.html might be interfering
   
2. **Check for flash messages:**
   - Look at the top of the page after form submission
   - Success messages appear in green
   - Error messages appear in red

3. **Check server logs:**
   - Look at the terminal/command prompt where Flask is running
   - You should see log messages like:
     ```
     Form data received: ImmutableMultiDict([...])
     Parsed data - Name: ..., Roll: ..., Dept: ...
     ```

---

## How to Verify Everything is Working

### Step 1: Check Database Directly
```bash
python -c "from app import app, db, Student; app.app_context().push(); students = Student.query.all(); print(f'Total students: {len(students)}'); [print(f'{s.id}: {s.full_name} - {s.roll_number}') for s in students]"
```

### Step 2: Test Add Student
1. Go to `/students`
2. Fill in the form:
   - Name: "Jane Smith"
   - Roll Number: "TEST002"
   - Department: "ECE"
3. Click "Add Student"
4. **Look for green success message at top of page**
5. **Scroll down to see student in table**

### Step 3: Test Assign Product
1. Make sure you have products with quantity > 0
2. Find a student without a product
3. Click "Assign Product" button
4. Select a product from dropdown
5. Click "Assign Product" in modal
6. **Look for success message**
7. **Page should refresh and show product in student row**

---

## Debug Mode

### Enable Detailed Logging
The app already has debug logging enabled. Check the terminal output for:

```
[INFO] Form data received: ...
[INFO] Parsed data - Name: ..., Roll: ..., Dept: ...
[INFO] Assign product called for student_id: ...
```

### Check Flask Debug Mode
In `app.py`, the last line should be:
```python
app.run(debug=True)
```

This enables:
- Auto-reload on code changes
- Detailed error messages
- Interactive debugger

---

## Quick Fixes

### Fix 1: Restart Everything
```bash
# Stop the Flask server (Ctrl + C)
# Then run:
python app.py
```

### Fix 2: Clear Browser and Retry
1. Close all browser tabs with the app
2. Clear browser cache
3. Open new tab
4. Go to `http://127.0.0.1:5000`
5. Login again
6. Try adding student

### Fix 3: Check Network Tab
1. Press F12 in browser
2. Go to "Network" tab
3. Submit the form
4. Look for `/add_student` request
5. Click on it
6. Check "Response" tab
7. Should see the student_details.html page

---

## What's Actually Happening

### When You Submit Student Form:
1. ✅ Form data is sent to `/add_student`
2. ✅ Route receives the data
3. ✅ Data is parsed correctly
4. ✅ Student is created in database
5. ✅ Database commit succeeds
6. ✅ Flash message is set
7. ✅ Redirect to `/students` happens
8. ❓ **Browser should show updated page with new student**

### If Student Doesn't Appear:
- The issue is likely in step 8 (browser display)
- **Not** a backend issue
- **Not** a database issue
- Likely a caching or JavaScript issue

---

## Recommended Actions

### Action 1: Test with Browser DevTools Open
1. Press F12
2. Go to Console tab
3. Submit form
4. Watch for any errors
5. Check Network tab for the POST request

### Action 2: Disable JavaScript Temporarily
1. In student_details.html, comment out the script at the bottom:
```html
<!--
<script>
  document.getElementById('studentForm').addEventListener('submit', function() {
    setTimeout(() => {
      this.reset();
    }, 100);
  });
</script>
-->
```

### Action 3: Add Alert for Debugging
Add this to the form in student_details.html:
```html
<form id="studentForm" action="/add_student" method="POST" onsubmit="alert('Form submitting!');">
```

---

## Success Indicators

### You'll Know It's Working When:
1. ✅ Green success message appears at top
2. ✅ Student appears in table below
3. ✅ Form fields are cleared
4. ✅ No error messages

### For Product Assignment:
1. ✅ Modal closes automatically
2. ✅ Success message appears
3. ✅ Product name appears in student row
4. ✅ "Assign Product" button changes to "Return" button

---

## Still Not Working?

### Last Resort Steps:
1. **Delete the database and recreate:**
   ```bash
   # Backup first!
   python init_database.py
   ```

2. **Check if another Flask instance is running:**
   - Look for other command prompts/terminals
   - Close them all
   - Start fresh

3. **Try a different browser:**
   - Chrome
   - Firefox
   - Edge

4. **Check firewall/antivirus:**
   - Make sure port 5000 is not blocked
   - Temporarily disable antivirus

---

## Contact Information

If none of these solutions work, provide:
1. Screenshot of browser console (F12 → Console tab)
2. Screenshot of Network tab showing the POST request
3. Copy of terminal output when submitting form
4. Browser and version you're using

---

**Remember:** The backend IS working! The routes are processing correctly. The issue is likely in the frontend display or browser caching.
