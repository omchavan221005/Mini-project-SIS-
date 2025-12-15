# Store Inventory Management System

A Flask-based web application for managing inventory and tracking product assignments to students.

## Features

- **User Authentication**
  - Secure login system
  - Role-based access control (Admin/User)
  - Session management

- **Inventory Management**
  - Add, edit, and delete products
  - Track product quantities and stock levels
  - Categorize products
  - Low stock alerts

- **Student Management**
  - Maintain student records
  - Assign products to students
  - Track product assignments and returns
  - View assignment history

- **Reporting**
  - Inventory status
  - Assignment history
  - Activity logs

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git (optional, for version control)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/store-inventory-system.git
   cd store-inventory-system
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   python init_database.py
   ```
   This will:
   - Create the SQLite database file
   - Create an admin user (username: admin, password: admin)
   - Add sample data for testing

5. **Configure environment variables**
   Create a `.env` file in the project root with the following content:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///inventory.db
   ```

## Running the Application

1. **Start the development server**
   ```bash
   flask run
   ```
   or
   ```bash
   python app.py
   ```

2. **Access the application**
   Open your web browser and go to: http://localhost:5000

## Default Login Credentials

- **Admin User**
  - Username: admin
  - Password: admin

## Project Structure

```
store-inventory-system/
├── app.py                  # Main application file
├── models.py               # Database models
├── init_db.py              # Database initialization script
├── requirements.txt        # Python dependencies
├── config.py               # Configuration settings
├── .env                    # Environment variables
├── logs/                   # Application logs
├── uploads/                # File uploads
└── templates/              # HTML templates
    ├── base.html           # Base template
    ├── index.html          # Dashboard
    ├── login.html          # Login page
    ├── store.html          # Inventory management
    ├── student_details.html # Student management
    ├── reports.html        # Reports
    └── 404.html            # 404 error page
```

## API Endpoints

### Authentication
- `POST /login` - User login
- `GET /logout` - User logout

### Products
- `GET /store` - View all products
- `POST /add_product` - Add a new product
- `POST /update_product` - Update a product
- `POST /delete_product/<int:product_id>` - Delete a product

### Students
- `GET /students` - View all students
- `POST /add_student` - Add a new student
- `POST /assign_product/<int:student_id>` - Assign product to student
- `POST /return_product/<int:student_id>` - Return product from student

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For support, please open an issue in the GitHub repository.
