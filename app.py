from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecret"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

# Dummy login credentials
USER = {"username": "admin", "password": "admin"}

# Database models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_of_issue = db.Column(db.Date, nullable=False)
    date_of_return = db.Column(db.Date, nullable=True)
    is_assigned = db.Column(db.Boolean, default=False)  # Track if product is assigned to a student

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(20), nullable=False, unique=True)
    department = db.Column(db.String(10), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='SET NULL'), nullable=True)
    assignment_date = db.Column(db.Date, nullable=True)  # When the product was assigned
    
    # Relationship with Product
    product = db.relationship('Product', backref='students')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        if username == USER["username"] and password == USER["password"]:
            session['user'] = username
            return redirect(url_for('index'))  # Go to index.html
        else:
            return render_template("login.html", error=True)

    return render_template("login.html")

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Add product
@app.route('/add', methods=['POST'])
def add():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        name = request.form['name']
        quantity = request.form['quantity']
        
        # Convert date strings to Python date objects
        date_of_issue = datetime.strptime(request.form['date_of_issue'], '%Y-%m-%d').date()
        
        # Handle optional return date
        date_of_return = None
        if request.form.get('date_of_return'):
            date_of_return = datetime.strptime(request.form['date_of_return'], '%Y-%m-%d').date()
        
        new_product = Product(name=name, quantity=quantity, date_of_issue=date_of_issue, date_of_return=date_of_return)
        db.session.add(new_product)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding product: {e}")
        
    return redirect(url_for('index'))

# Delete product
@app.route('/delete/<int:id>')
def delete(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    product = Product.query.get(id)
    if product:
        # Remove product assignment from students before deleting
        students_with_product = Student.query.filter_by(product_id=id).all()
        for student in students_with_product:
            student.product_id = None
        
        db.session.delete(product)
        db.session.commit()
    
    return redirect(url_for('index'))

# Add student
@app.route('/add_student', methods=['POST'])
def add_student():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        full_name = request.form['fullName']
        roll_number = request.form['rollNumber']
        department = request.form['department']
        product_name = request.form.get('productName')  # Product name instead of ID
        quantity = request.form.get('quantity', 1)  # Quantity (default 1)
        
        new_student = Student(
            full_name=full_name,
            roll_number=roll_number,
            department=department,
            product_id=None,
            assignment_date=None
        )
        
        # If product name is provided, create a unique product instance for this student
        if product_name:
            # Create a new unique product instance for this student
            new_product = Product(
                name=product_name,
                quantity=int(quantity),
                date_of_issue=datetime.now().date(),
                date_of_return=None,
                is_assigned=True
            )
            db.session.add(new_product)
            db.session.flush()  # Get the ID of the new product
            
            # Assign the product to the student
            new_student.product_id = new_product.id
            new_student.assignment_date = datetime.now().date()
        
        db.session.add(new_student)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding student: {e}")
        # You could add flash message here for user feedback
        
    return redirect(url_for('students'))

# Assign existing product from inventory to student
@app.route('/assign_product/<int:student_id>', methods=['POST'])
def assign_product(student_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        student = Student.query.get(student_id)
        if not student:
            return redirect(url_for('students'))
        
        product_id = request.form.get('productId')
        if product_id:
            product = Product.query.get(product_id)
            if product and not product.is_assigned:
                # Create a unique copy of this product for the student
                new_product = Product(
                    name=product.name,
                    quantity=product.quantity,
                    date_of_issue=datetime.now().date(),
                    date_of_return=None,
                    is_assigned=True
                )
                db.session.add(new_product)
                db.session.flush()
                
                # Assign to student
                student.product_id = new_product.id
                student.assignment_date = datetime.now().date()
                
                db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error assigning product: {e}")
        
    return redirect(url_for('students'))

# Delete student
@app.route('/delete_student/<int:id>')
def delete_student(id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    try:
        student = Student.query.get(id)
        if student and student.product:
            # Delete the unique product instance assigned to this student
            product = student.product
            db.session.delete(student)
            db.session.delete(product)
            db.session.commit()
        elif student:
            # Student has no product, just delete the student
            db.session.delete(student)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting student: {e}")
        
    return redirect(url_for('students'))

# Index (protected page) - Store Inventory
@app.route('/')
def index():
    if 'user' not in session:   # Not logged in → redirect
        return redirect(url_for('login'))

    products = Product.query.all()
    return render_template("index.html", products=products)

# Student Details page (protected page)
@app.route('/students')
def students():
    if 'user' not in session:   # Not logged in → redirect
        return redirect(url_for('login'))
    
    students_list = Student.query.all()
    # Only show unassigned products for new assignments
    available_products = Product.query.filter_by(is_assigned=False).all()
    return render_template("student_details.html", students=students_list, products=available_products)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
