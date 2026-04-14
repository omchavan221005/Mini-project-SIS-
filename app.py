from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect, generate_csrf
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Email, Optional, Length
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
import json
import csv
import io
import os
from twilio.rest import Client
from flask_mail import Mail, Message
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from collections import Counter
from werkzeug.utils import secure_filename

# Optional imports for Excel functionality
try:
    import pandas as pd
    EXCEL_SUPPORT = True
except ImportError:
    EXCEL_SUPPORT = False
    pd = None

# Initialize Flask app
app = Flask(__name__)
load_dotenv()

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-change-this-in-production'
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# File Uploads - Use /tmp on Vercel as only that is writable
if os.environ.get('VERCEL'):
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
else:
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Email/SMS configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Helper function to send SMS
def send_sms(to_number, message_body):
    """Utility to send SMS via Twilio"""
    if not os.environ.get('TWILIO_ACCOUNT_SID'):
        app.logger.warning('Twilio credentials not found. SMS not sent.')
        return False
        
    try:
        # Format phone number for Twilio (ensure it starts with +)
        if to_number and not to_number.startswith('+'):
            # Default to India (+91) if not provided, or you can change this
            to_number = '+91' + to_number.strip().lstrip('0')
            
        client = Client(
            os.environ.get('TWILIO_ACCOUNT_SID'),
            os.environ.get('TWILIO_AUTH_TOKEN')
        )
        
        message = client.messages.create(
            from_=os.environ.get('TWILIO_PHONE_NUMBER'),
            body=message_body,
            to=to_number
        )
        app.logger.info(f'SMS sent successfully to {to_number}: {message.sid}')
        return True
    except Exception as e:
        app.logger.error(f'Failed to send SMS to {to_number}: {str(e)}')
        return False

def send_email(subject, recipient, body):
    try:
        if not app.config['MAIL_USERNAME']: return False
        msg = Message(subject, recipients=[recipient], body=body)
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error(f"Email Error: {str(e)}")
    return False

# Configure logging
if not app.debug:
    # On Vercel or production, log to stdout rather than a file
    if os.environ.get('VERCEL') or os.environ.get('LOG_TO_STDOUT'):
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/campuskart.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    
    app.logger.setLevel(logging.INFO)
    app.logger.info('CampusKart Startup')

# Initialize database tables
with app.app_context():
    try:
        db.create_all()
        app.logger.info('Database tables verified/created.')
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin')
            admin = User(username='admin', is_admin=True)
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            app.logger.info(f'Created admin user with username: admin')
    except Exception as e:
        app.logger.error(f'Database initialization error: {str(e)}')

# Database Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    min_stock_level = db.Column(db.Integer, default=5, nullable=False)
    category = db.Column(db.String(50), nullable=True)
    date_of_issue = db.Column(db.Date, nullable=True)
    is_assigned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('ProductAssignment', backref='product', lazy=True)
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.min_stock_level

class ProductAssignment(db.Model):
    __tablename__ = 'product_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    returned_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='assigned')
    quantity = db.Column(db.Integer, nullable=False, default=1)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    student = db.relationship('Student', backref='assignments', lazy=True)

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(50), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    assignment_date = db.Column(db.Date, nullable=True)
    return_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    current_product = db.relationship('Product', foreign_keys=[product_id], backref='current_holders', lazy=True)

# Forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(min=2, max=100)])
    category = SelectField('Category', choices=[
        ('Electronics', 'Electronics'),
        ('Stationery', 'Stationery'),
        ('Furniture', 'Furniture'),
        ('Lab Equipment', 'Lab Equipment'),
        ('Sports', 'Sports'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[
        DataRequired(),
        NumberRange(min=0, message='Quantity cannot be negative')
    ])
    min_stock_level = IntegerField('Minimum Stock Level', validators=[
        DataRequired(),
        NumberRange(min=1, message='Minimum stock level must be at least 1')
    ])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save')

class StudentForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    roll_number = StringField('Roll Number', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    department = StringField('Department', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Save')

# Authentication Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_admin' not in session or not session['is_admin']:
            flash('You do not have permission to access this page.', 'danger')
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

# Helper Functions
def log_activity(user_id, action, details=None):
    """Log user activity to the database."""
    try:
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        app.logger.error(f'Error logging activity: {str(e)}')
        db.session.rollback()

# Routes
@app.route('/')
@login_required
def index():
    # Dashboard statistics
    total_products = Product.query.count()
    total_students = Student.query.count()
    total_quantity = db.session.query(db.func.sum(Product.quantity)).scalar() or 0
    active_assignments = ProductAssignment.query.filter_by(status='assigned').count()
    low_stock_count = Product.query.filter(Product.quantity <= Product.min_stock_level).count()
    
    # Recent activity
    recent_assignments = ProductAssignment.query.order_by(
        ProductAssignment.assigned_date.desc()
    ).limit(5).all()
    
    # Low stock products
    low_stock_products = Product.query.filter(
        Product.quantity <= Product.min_stock_level
    ).limit(5).all()
    
    # Top categories
    products_by_category = db.session.query(
        Product.category,
        db.func.count(Product.id).label('count')
    ).group_by(Product.category).all()
    
    return render_template(
        'dashboard.html',
        total_products=total_products,
        total_students=total_students,
        total_quantity=total_quantity,
        active_assignments=active_assignments,
        low_stock_count=low_stock_count,
        recent_assignments=recent_assignments,
        low_stock_products=low_stock_products,
        products_by_category=products_by_category
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # 1. Look for user in database
        user = User.query.filter_by(username=username).first()
        
        # 2. Verify existence and match password hash
        if user and user.check_password(password):
            # 3. Establish session state
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            session.permanent = True
            
            # 4. Update last login timestamp
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            log_activity(user.id, 'login', f'User {username} authenticated successfully')
            flash(f'Welcome back, {username}! Authorization granted.', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            # 5. Handle authentication failure
            log_activity(0, 'auth_fail', f'Failed login attempt for user: {username}')
            flash('Authentication error: Invalid access key or user identity.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    log_activity(session.get('user_id'), 'logout', f'User {session.get("username")} logged out')
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/store')
@login_required
def store():
    products = Product.query.all()
    total_items = sum(p.quantity for p in products)
    low_stock_count = len([p for p in products if p.is_low_stock])
    assigned_items_count = len([p for p in products if p.is_assigned])
    
    return render_template(
        'store.html',
        products=products,
        total_items=total_items,
        low_stock_count=low_stock_count,
        assigned_items_count=assigned_items_count,
        form=ProductForm(),
        excel_support=EXCEL_SUPPORT
    )

@app.route('/add_product', methods=['POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        try:
            product = Product(
                name=form.name.data,
                category=form.category.data,
                quantity=form.quantity.data,
                min_stock_level=form.min_stock_level.data,
                description=form.description.data,
                date_of_issue=datetime.utcnow().date(),
                is_assigned=False
            )
            db.session.add(product)
            db.session.commit()
            
            log_activity(session['user_id'], 'add_product', f'Added product: {product.name}')
            flash('Product added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error adding product: {str(e)}')
            flash('Error adding product. Please try again.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{form[field].label.text}: {error}', 'danger')
    
    return redirect(url_for('store'))

@app.route('/update_product', methods=['POST'])
@login_required
def update_product():
    form = ProductForm()
    if form.validate_on_submit():
        try:
            product_id = request.form.get('product_id')
            if not product_id:
                flash('Product ID is missing', 'danger')
                return redirect(url_for('store'))
                
            product = Product.query.get_or_404(product_id)
            old_quantity = product.quantity
            
            product.name = form.name.data
            product.category = form.category.data
            product.quantity = form.quantity.data
            product.min_stock_level = form.min_stock_level.data
            product.description = form.description.data
            
            db.session.commit()
            
            # Log quantity changes
            if old_quantity != product.quantity:
                log_activity(
                    session['user_id'],
                    'update_quantity',
                    f'Updated quantity for {product.name} from {old_quantity} to {product.quantity}'
                )
            
            log_activity(session['user_id'], 'update_product', f'Updated product: {product.name}')
            flash('Product updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error updating product: {str(e)}')
            flash('Error updating product. Please try again.', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{form[field].label.text}: {error}', 'danger')
    
    return redirect(url_for('store'))

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        product_name = product.name
        
        # Check if product is assigned to any student
        active_assignments = ProductAssignment.query.filter_by(
            product_id=product_id,
            status='assigned'
        ).count()
        
        if active_assignments > 0:
            flash(f'Cannot delete {product_name} as it is currently assigned to {active_assignments} student(s).', 'danger')
            return redirect(url_for('store'))
        
        db.session.delete(product)
        db.session.commit()
        
        log_activity(session['user_id'], 'delete_product', f'Deleted product: {product_name}')
        flash(f'Product "{product_name}" has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting product: {str(e)}')
        flash('Error deleting product. Please try again.', 'danger')
    
    return redirect(url_for('store'))

@app.route('/students')
@login_required
def students():
    students_list = Student.query.all()
    available_products = Product.query.filter(Product.quantity > 0).all()
    return render_template("student_details.html", students=students_list, products=available_products)

@app.route('/add_student', methods=['POST'])
@login_required
@csrf.exempt  # Temporarily exempt to test
def add_student():
    try:
        # Debug: Log all form data
        app.logger.info(f'Form data received: {request.form}')
        
        # Get form data directly from request
        full_name = request.form.get('fullName')
        roll_number = request.form.get('rollNumber')
        department = request.form.get('department')
        email = request.form.get('email', '').strip() or None
        phone = request.form.get('phone', '').strip() or None
        
        app.logger.info(f'Parsed data - Name: {full_name}, Roll: {roll_number}, Dept: {department}, Email: {email}')
        
        # Validate required fields
        if not full_name or not roll_number or not department:
            flash('Please fill in all required fields (Name, Roll Number, Department).', 'danger')
            return redirect(url_for('students'))
        
        # Check if roll number already exists
        existing_student = Student.query.filter_by(roll_number=roll_number).first()
        if existing_student:
            flash(f'A student with roll number {roll_number} already exists!', 'danger')
            return redirect(url_for('students'))
        
        # Create new student
        student = Student(
            full_name=full_name,
            roll_number=roll_number,
            email=email,
            phone=phone,
            department=department
        )
        db.session.add(student)
        db.session.commit()
        
        log_activity(session['user_id'], 'add_student', f'Added student: {student.full_name}')
        flash(f'Student {full_name} added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error adding student: {str(e)}')
        flash(f'Error adding student: {str(e)}', 'danger')
    
    return redirect(url_for('students'))

@app.route('/delete_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_student(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        
        # Check if student has active assignments
        active_assignments = ProductAssignment.query.filter_by(
            student_id=student.id,
            status='assigned'
        ).count()
        
        if active_assignments > 0:
            flash(f'Cannot delete student {student.full_name} because they have {active_assignments} active product assignment(s). Please return all products first.', 'danger')
            return redirect(url_for('students'))
            
        student_name = student.full_name
        
        # Delete related assignment history (since student_id is not nullable)
        # Using a more direct delete approach to ensure database integrity
        ProductAssignment.query.filter_by(student_id=student.id).delete()
        
        db.session.delete(student)
        db.session.commit()
        
        log_activity(session.get('user_id', 0), 'delete_student', f'Deleted student record for {student_name}')
        flash(f'Student {student_name} has been successfully purged from the registry.', 'success')
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting student: {str(e)}")
        flash('An internal error occurred while trying to purge the record.', 'danger')
        
    return redirect(url_for('students'))

@app.route('/assign_product/<int:student_id>', methods=['POST'])
@login_required
@csrf.exempt  # Temporarily exempt to test
def assign_product(student_id):
    try:
        # Debug logging
        app.logger.info(f'Assign product called for student_id: {student_id}')
        app.logger.info(f'Is JSON: {request.is_json}, Form data: {request.form}')
        
        # Support both JSON and form data
        if request.is_json:
            data = request.get_json()
            product_id = data.get('product_id')
            assign_quantity = int(data.get('quantity', 1))
        else:
            product_id = request.form.get('productId')
            assign_quantity = int(request.form.get('quantity', 1))
        
        app.logger.info(f'Assign product called for student_id: {student_id}, Product: {product_id}, Quantity: {assign_quantity}')
        
        if not product_id:
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Product ID is required'
                }), 400
            else:
                flash('Product ID is required', 'danger')
                return redirect(url_for('students'))
            
        student = Student.query.get_or_404(student_id)
        product = Product.query.get_or_404(product_id)
        
        # Check if product is already assigned (if it's a single-item product)
        if product.is_assigned and product.quantity <= 1:
            if request.is_json:
                return jsonify({
                    'success': False, 
                    'message': f'This {product.name} is already assigned to another student.'
                }), 400
            else:
                flash(f'This {product.name} is already assigned to another student.', 'danger')
                return redirect(url_for('students'))
            
        # Check if product is in stock
        if product.quantity < assign_quantity:
            message = f'Sorry, only {product.quantity} units of {product.name} are available.'
            if request.is_json:
                return jsonify({'success': False, 'message': message}), 400
            else:
                flash(message, 'danger')
                return redirect(url_for('students'))
            
        # Decrement quantity
        product.quantity -= assign_quantity
        if product.quantity == 0:
            product.is_assigned = True
            
        # 3. Process Dates (Admin Input or Default)
        now = datetime.utcnow()
        due_date_str = request.form.get('dueDate') if not request.is_json else data.get('due_date')
        
        try:
            if due_date_str:
                due = datetime.strptime(due_date_str, '%Y-%m-%d')
            else:
                due = now + timedelta(days=7) # Default fallback
        except (ValueError, TypeError):
            due = now + timedelta(days=7)
            
        # 4. Finalize Database Record
        assignment = ProductAssignment(
            product_id=product.id,
            student_id=student.id,
            assigned_date=now,
            due_date=due,
            status='assigned',
            quantity=assign_quantity
        )
        
        db.session.add(assignment)
        
        # Update student's current product (Legacy support)
        student.product_id = product.id
        student.assignment_date = now.date()
        student.return_date = due.date()
        
        db.session.commit()
        
        # Send SMS Notification to Student
        if student.phone:
            sms_body = (
                f"Hello {student.full_name}, \n"
                f"Product Assigned: {product.name} (x{assign_quantity})\n"
                f"Assigned Date: {now.strftime('%Y-%m-%d')}\n"
                f"Due Date: {due.strftime('%Y-%m-%d')}\n"
                f"Please ensure it is returned on time."
            )
            send_sms(student.phone, sms_body)
        
        # Log the assignment
        log_activity(
            session['user_id'],
            'assign_product',
            f'Assigned {product.name} to {student.full_name} (ID: {student.id})'
        )
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': f'{product.name} assigned to {student.full_name} successfully!',
                'remaining_quantity': product.quantity
            })
        else:
            flash(f'{product.name} (x{assign_quantity}) assigned to {student.full_name} successfully!', 'success')
            return redirect(url_for('student_history', student_id=student.id))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error assigning product: {str(e)}')
        if request.is_json:
            return jsonify({
                'success': False,
                'message': 'An error occurred while assigning the product.'
            }), 500
        else:
            flash('An error occurred while assigning the product.', 'danger')
            return redirect(url_for('students'))

@app.route('/return_product/<int:student_id>', methods=['POST'])
@login_required
def return_product(student_id):
    try:
        student = Student.query.get_or_404(student_id)
        product_id = request.form.get('productId')
        
        if not product_id:
            # Fallback to old behavior if needed, but better to require ID
            return jsonify({'success': False, 'message': 'Product ID not specified'}), 400
            
        product = Product.query.get(product_id)
        
        # Update specific assignment status
        assignment = ProductAssignment.query.filter_by(
            product_id=product_id,
            student_id=student.id,
            status='assigned'
        ).order_by(ProductAssignment.assigned_date.desc()).first()
        
        if assignment:
            assignment.returned_date = datetime.utcnow()
            assignment.status = 'returned'
            return_quantity = assignment.quantity
        else:
            return_quantity = 1
        
        # Update product quantity
        if product:
            product.quantity += return_quantity  # Increase quantity by the amount returned
            if product.quantity > 0:
                product.is_assigned = False
        
        # Update student record
        student.product_id = None
        student.assignment_date = None
        student.return_date = datetime.utcnow().date()
        
        db.session.commit()
        
        # Log the return
        log_activity(
            session['user_id'],
            'return_product',
            f'Returned {product.name if product else "item"} from {student.full_name} (ID: {student.id})'
        )
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': f'Product returned successfully from {student.full_name}.',
                'updated_quantity': product.quantity if product else 0
            })
        else:
            flash(f'Product returned successfully from {student.full_name}.', 'success')
            return redirect(url_for('student_history', student_id=student.id))
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error returning product: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'An error occurred while processing the return.'
        }), 500

@app.route('/student/<int:student_id>')
@login_required
def student_history(student_id):
    student = Student.query.get_or_404(student_id)
    # Get all assignments for this student, ordered by most recent
    assignments = ProductAssignment.query.filter_by(student_id=student.id).order_by(ProductAssignment.assigned_date.desc()).all()
    available_products = Product.query.filter(Product.quantity > 0).all()
    
    return render_template('student_history.html', 
                         student=student, 
                         assignments=assignments,
                         products=available_products)

@app.route('/notifications/send_overdue_reminders')
@login_required
def send_overdue_reminders():
    """Manual trigger to send SMS reminders to all students with overdue items"""
    try:
        now = datetime.utcnow()
        overdue_assignments = ProductAssignment.query.filter(
            ProductAssignment.status == 'assigned',
            ProductAssignment.due_date < now
        ).all()
        
        sent_count = 0
        for assignment in overdue_assignments:
            student = assignment.student
            if student.phone:
                days_overdue = (now - assignment.due_date).days
                sms_body = (
                    f"URGENT: {student.full_name}, your assignment of "
                    f"{assignment.product.name} (x{assignment.quantity}) was due on "
                    f"{assignment.due_date.strftime('%Y-%m-%d')}. "
                    f"It is now {days_overdue} day(s) overdue. Please return it immediately."
                )
                if send_sms(student.phone, sms_body):
                    sent_count += 1
        
        flash(f'Successfully sent {sent_count} overdue reminders.', 'success')
        return redirect(url_for('notifications'))
    except Exception as e:
        app.logger.error(f'Error sending reminders: {str(e)}')
        flash('An error occurred while sending reminders.', 'danger')
        return redirect(url_for('notifications'))
@app.route('/notifications')
@login_required
def notifications():
    """Enhanced notification center with all date-related system updates"""
    notifications = []
    now = datetime.utcnow()
    
    # 1. Low stock notifications
    low_stock_products = Product.query.filter(Product.quantity <= Product.min_stock_level).all()
    for product in low_stock_products:
        notifications.append({
            'title': 'Low Stock Alert',
            'message': f'{product.name} is low on stock ({product.quantity} remaining).',
            'type': 'warning',
            'created_at': product.created_at or now
        })
        
    # 2. Overdue Assignment notifications
    overdue = ProductAssignment.query.filter(
        ProductAssignment.status == 'assigned',
        ProductAssignment.due_date < now
    ).all()
    for assignment in overdue:
        notifications.append({
            'title': 'Overdue Item',
            'message': f'{assignment.student.full_name} has not returned {assignment.product.name} (Due: {assignment.due_date.strftime("%Y-%m-%d")})',
            'type': 'error',
            'created_at': assignment.due_date
        })
        
    # 3. Due Soon notifications (Next 48 hours)
    soon = ProductAssignment.query.filter(
        ProductAssignment.status == 'assigned',
        ProductAssignment.due_date >= now,
        ProductAssignment.due_date <= now + timedelta(hours=48)
    ).all()
    for assignment in soon:
        notifications.append({
            'title': 'Due Soon',
            'message': f'{assignment.product.name} assigned to {assignment.student.full_name} is due on {assignment.due_date.strftime("%Y-%m-%d")}',
            'type': 'info',
            'created_at': assignment.assigned_date
        })
        
    # 4. Recent activity from last 24 hours (New assignments/returns)
    recent_activity = ProductAssignment.query.filter(
        (ProductAssignment.assigned_date >= now - timedelta(hours=24)) |
        (ProductAssignment.returned_date >= now - timedelta(hours=24))
    ).all()
    for activity in recent_activity:
        if activity.status == 'assigned':
            notifications.append({
                'title': 'New Assignment',
                'message': f'{activity.product.name} (x{activity.quantity}) assigned to {activity.student.full_name}',
                'type': 'success',
                'created_at': activity.assigned_date
            })
        elif activity.status == 'returned' and activity.returned_date:
            notifications.append({
                'title': 'Item Returned',
                'message': f'{activity.student.full_name} returned {activity.product.name}',
                'type': 'success',
                'created_at': activity.returned_date
            })

    # Sort notifications by date (newest first)
    notifications.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('notifications.html', notifications=notifications)

# Reports
@app.route('/reports')
@login_required
def reports():
    # Get statistics
    total_products = Product.query.count()
    total_students = Student.query.count()
    assigned_products = ProductAssignment.query.filter_by(status='assigned').count()
    low_stock_products = Product.query.filter(Product.quantity <= Product.min_stock_level).count()
    
    # Get products by category
    category_counts = db.session.query(
        Product.category,
        db.func.count(Product.id).label('count')
    ).group_by(Product.category).all()
    
    category_data = {category: count for category, count in category_counts}
    
    # Get students by department
    department_counts = db.session.query(
        Student.department,
        db.func.count(Student.id).label('count')
    ).group_by(Student.department).all()
    
    department_data = {dept: count for dept, count in department_counts if dept}
    
    # Recent assignments count (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_assignments = ProductAssignment.query.filter(
        ProductAssignment.assigned_date >= thirty_days_ago
    ).count()
    
    return render_template('reports.html',
                         total_products=total_products,
                         total_students=total_students,
                         assigned_products=assigned_products,
                         low_stock_products=low_stock_products,
                         category_data=json.dumps(category_data),
                         department_data=json.dumps(department_data),
                         recent_assignments=recent_assignments)

# API endpoint for analytics
@app.route('/api/analytics')
@login_required
def api_analytics():
    """API endpoint for real-time analytics data"""
    # Generate mock stock trend data for last 30 days
    stock_trend = []
    for i in range(30, 0, -1):
        date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
        # Get total stock for that day (simplified - using current stock)
        total_stock = db.session.query(db.func.sum(Product.quantity)).scalar() or 0
        stock_trend.append({
            'date': date,
            'stock': total_stock + (i * 2)  # Simulate historical data
        })
    
    return jsonify({
        'stock_trend': stock_trend
    })

# Export routes
@app.route('/export/products')
@login_required
def export_products():
    """Export products to CSV"""
    import io
    from flask import make_response
    
    # Get all products
    products = Product.query.all()
    
    # Create CSV
    output = io.StringIO()
    output.write('ID,Name,Category,Quantity,Min Stock Level,Description,Date of Issue,Status\n')
    
    for product in products:
        status = 'Low Stock' if product.is_low_stock else 'In Stock'
        output.write(f'{product.id},{product.name},{product.category},{product.quantity},'
                    f'{product.min_stock_level},"{product.description or ""}",{product.date_of_issue},{status}\n')
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=products_export.csv'
    response.headers['Content-Type'] = 'text/csv'
    
    return response

@app.route('/export/students')
@login_required
def export_students():
    """Export students to CSV"""
    import io
    from flask import make_response
    
    # Get all students
    students = Student.query.all()
    
    # Create CSV
    output = io.StringIO()
    output.write('ID,Full Name,Roll Number,Email,Phone,Department,Assigned Product,Assignment Date\n')
    
    for student in students:
        product_name = student.current_product.name if student.product_id and student.current_product else 'None'
        assignment_date = student.assignment_date if student.assignment_date else 'N/A'
        output.write(f'{student.id},{student.full_name},{student.roll_number},'
                    f'{student.email or "N/A"},{student.phone or "N/A"},{student.department or "N/A"},'
                    f'{product_name},{assignment_date}\n')
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=students_export.csv'
    response.headers['Content-Type'] = 'text/csv'
    
    return response


# Settings
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """Route to handle password changes"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    print(f"[DEBUG] Password change attempt for user_id: {session.get('user_id')}")
    
    # 1. Basic validation
    if not current_password or not new_password or not confirm_password:
        flash('All fields are required to update your security credentials.', 'danger')
        return redirect(url_for('settings', tab='user'))
        
    if new_password != confirm_password:
        flash('Password mismatch: The new password and confirmation do not match.', 'danger')
        return redirect(url_for('settings', tab='user'))
    
    # 2. Get current user (Using modern SQLAlchemy get method)
    user_id = session.get('user_id')
    user = db.session.get(User, user_id)
    
    if not user:
        print(f"[ERROR] User not found during password change. user_id: {user_id}")
        flash('Session invalid. Please log in again.', 'danger')
        return redirect(url_for('logout'))
    
    # 3. Verify current password
    if not user.check_password(current_password):
        print(f"[ERROR] Incorrect current password for user: {user.username}")
        flash('Authorization failed: Incorrect current password.', 'danger')
        return redirect(url_for('settings', tab='user'))
        
    try:
        # 4. Apply new password
        user.set_password(new_password)
        db.session.commit()
        print(f"[SUCCESS] Password updated for user: {user.username}")
        
        # 5. Log activity and redirect
        log_activity(user_id, 'change_password', f'User {user.username} successfully updated their access key')
        flash('Security upgrade complete: Your password has been successfully updated.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"[FATAL] Error updating password: {str(e)}")
        flash('A system error occurred. Password change failed.', 'danger')
        
    return redirect(url_for('settings', tab='user'))

# Activity Logs
@app.route('/activity_logs')
@login_required
@admin_required
def activity_logs():
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(page=page, per_page=20)
    return render_template('activity_logs.html', logs=logs)

# Excel Upload Routes
@app.route('/download_template')
@login_required
def download_template():
    """Download sample Excel template for product import"""
    if not EXCEL_SUPPORT:
        flash('Excel support not available. Please install pandas and openpyxl.', 'warning')
        return redirect(url_for('store'))
    
    from flask import make_response
    
    try:
        # Create sample data
        sample_data = {
            'Product Name': ['Laptop', 'Mouse', 'Keyboard'],
            'Category': ['Electronics', 'Electronics', 'Electronics'],
            'Quantity': [10, 50, 30],
            'Min Stock Level': [5, 10, 10],
            'Description': ['Dell Laptop 15 inch', 'Wireless Mouse', 'Mechanical Keyboard']
        }
        
        df = pd.DataFrame(sample_data)
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Products')
        
        output.seek(0)
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=product_import_template.xlsx'
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        log_activity(session['user_id'], 'download_template', 'Downloaded product import template')
        
        return response
    except Exception as e:
        app.logger.error(f'Error creating template: {str(e)}')
        flash('Error creating template file.', 'danger')
        return redirect(url_for('store'))

@app.route('/upload_excel', methods=['POST'])
@login_required
def upload_excel():
    """Handle Excel file upload and parsing"""
    if not EXCEL_SUPPORT:
        return jsonify({
            'success': False,
            'message': 'Excel support not available. Please install pandas and openpyxl: pip install pandas openpyxl'
        }), 503
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Check file extension
        allowed_extensions = {'.xlsx', '.xls', '.csv'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'message': 'Invalid file format. Please upload .xlsx, .xls, or .csv file'
            }), 400
        
        # Read file based on extension
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error reading file: {str(e)}'
            }), 400
        
        # Validate required columns
        required_columns = ['Product Name', 'Category', 'Quantity', 'Min Stock Level']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return jsonify({
                'success': False,
                'message': f'Missing required columns: {", ".join(missing_columns)}'
            }), 400
        
        # Validate and parse data
        parsed_data = []
        errors = []
        
        for index, row in df.iterrows():
            row_num = index + 2  # +2 because Excel is 1-indexed and has header
            row_errors = []
            
            # Validate Product Name
            if pd.isna(row['Product Name']) or str(row['Product Name']).strip() == '':
                row_errors.append(f'Row {row_num}: Product Name is required')
            
            # Validate Category
            valid_categories = ['Electronics', 'Stationery', 'Furniture', 'Lab Equipment', 'Sports', 'Other']
            category = str(row['Category']).strip() if not pd.isna(row['Category']) else ''
            if category not in valid_categories:
                row_errors.append(f'Row {row_num}: Invalid category. Must be one of: {", ".join(valid_categories)}')
            
            # Validate Quantity
            try:
                quantity = int(row['Quantity'])
                if quantity < 0:
                    row_errors.append(f'Row {row_num}: Quantity cannot be negative')
            except (ValueError, TypeError):
                row_errors.append(f'Row {row_num}: Quantity must be a valid number')
                quantity = 0
            
            # Validate Min Stock Level
            try:
                min_stock = int(row['Min Stock Level'])
                if min_stock < 1:
                    row_errors.append(f'Row {row_num}: Min Stock Level must be at least 1')
            except (ValueError, TypeError):
                row_errors.append(f'Row {row_num}: Min Stock Level must be a valid number')
                min_stock = 5
            
            # Get description (optional)
            description = str(row.get('Description', '')).strip() if not pd.isna(row.get('Description')) else ''
            
            if row_errors:
                errors.extend(row_errors)
            else:
                parsed_data.append({
                    'name': str(row['Product Name']).strip(),
                    'category': category,
                    'quantity': quantity,
                    'min_stock_level': min_stock,
                    'description': description,
                    'row_number': row_num
                })
        
        # Return parsed data and errors for preview
        return jsonify({
            'success': True,
            'data': parsed_data,
            'errors': errors,
            'total_rows': len(df),
            'valid_rows': len(parsed_data),
            'error_count': len(errors)
        })
        
    except Exception as e:
        app.logger.error(f'Error uploading Excel file: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'An error occurred while processing the file: {str(e)}'
        }), 500

@app.route('/import_excel_data', methods=['POST'])
@login_required
def import_excel_data():
    """Import validated Excel data into database"""
    if not EXCEL_SUPPORT:
        return jsonify({
            'success': False,
            'message': 'Excel support not available. Please install pandas and openpyxl.'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or 'products' not in data:
            return jsonify({
                'success': False,
                'message': 'No data provided for import'
            }), 400
        
        products_data = data['products']
        imported_count = 0
        failed_count = 0
        errors = []
        
        for product_data in products_data:
            try:
                # Check if product with same name already exists
                existing_product = Product.query.filter_by(name=product_data['name']).first()
                
                if existing_product:
                    # Update existing product quantity
                    existing_product.quantity += product_data['quantity']
                    existing_product.category = product_data['category']
                    existing_product.min_stock_level = product_data['min_stock_level']
                    if product_data.get('description'):
                        existing_product.description = product_data['description']
                    
                    log_activity(
                        session['user_id'],
                        'update_product_import',
                        f'Updated {existing_product.name} via Excel import (added {product_data["quantity"]} units)'
                    )
                else:
                    # Create new product
                    product = Product(
                        name=product_data['name'],
                        category=product_data['category'],
                        quantity=product_data['quantity'],
                        min_stock_level=product_data['min_stock_level'],
                        description=product_data.get('description', ''),
                        date_of_issue=datetime.utcnow().date(),
                        is_assigned=False
                    )
                    db.session.add(product)
                    
                    log_activity(
                        session['user_id'],
                        'add_product_import',
                        f'Added {product.name} via Excel import'
                    )
                
                imported_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Failed to import {product_data['name']}: {str(e)}")
                app.logger.error(f"Error importing product {product_data['name']}: {str(e)}")
        
        # Commit all changes
        db.session.commit()
        
        log_activity(
            session['user_id'],
            'excel_import',
            f'Imported {imported_count} products from Excel file'
        )
        
        return jsonify({
            'success': True,
            'message': f'Successfully imported {imported_count} products',
            'imported_count': imported_count,
            'failed_count': failed_count,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error importing Excel data: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'An error occurred during import: {str(e)}'
        }), 500

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    db.session.rollback()
    app.logger.error(f'500 Error: {str(e)}')
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
