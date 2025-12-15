from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    activities = db.relationship('ActivityLog', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    
    def __repr__(self):
        return f'<ActivityLog {self.action} at {self.timestamp}>'

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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('ProductAssignment', back_populates='product', lazy=True)
    current_holder = db.relationship('Student', back_populates='product', uselist=False, foreign_keys='Student.product_id')
    
    def __repr__(self):
        return f'<Product {self.name} (ID: {self.id})>'
    
    @property
    def is_low_stock(self):
        """Check if the product quantity is at or below the minimum stock level."""
        return self.quantity <= self.min_stock_level
    
    def assign_to_student(self, student):
        """Assign this product to a student."""
        if self.quantity <= 0:
            raise ValueError("Product is out of stock")
            
        self.quantity -= 1
        self.is_assigned = (self.quantity == 0)
        
        assignment = ProductAssignment(
            product_id=self.id,
            student_id=student.id,
            assigned_date=datetime.utcnow(),
            status='assigned'
        )
        
        db.session.add(assignment)
        return assignment
    
    def return_from_student(self, student):
        """Return this product from a student."""
        assignment = ProductAssignment.query.filter_by(
            product_id=self.id,
            student_id=student.id,
            status='assigned'
        ).first()
        
        if not assignment:
            raise ValueError("No active assignment found for this product and student")
            
        assignment.returned_date = datetime.utcnow()
        assignment.status = 'returned'
        
        self.quantity += 1
        self.is_assigned = False
        
        return assignment

class ProductAssignment(db.Model):
    __tablename__ = 'product_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    returned_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='assigned')  # 'assigned' or 'returned'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', back_populates='assignments')
    student = db.relationship('Student', back_populates='assigned_products')
    
    def __repr__(self):
        return f'<ProductAssignment {self.id}: {self.product.name} -> {self.student.full_name}>'

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Current product assignment
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    assignment_date = db.Column(db.Date, nullable=True)
    return_date = db.Column(db.Date, nullable=True)
    
    # Relationships
    product = db.relationship('Product', back_populates='current_holder', foreign_keys=[product_id])
    assigned_products = db.relationship('ProductAssignment', back_populates='student', lazy=True)
    
    def __repr__(self):
        return f'<Student {self.full_name} ({self.roll_number})>'
    
    @property
    def current_assignment(self):
        """Get the current product assignment if any."""
        return ProductAssignment.query.filter_by(
            student_id=self.id,
            status='assigned'
        ).first()
    
    @property
    def assigned_products_history(self):
        """Get all product assignments for this student, ordered by assignment date."""
        return ProductAssignment.query.filter_by(
            student_id=self.id
        ).order_by(ProductAssignment.assigned_date.desc()).all()
    
    @property
    def has_active_assignment(self):
        """Check if the student currently has an assigned product."""
        return self.current_assignment is not None
