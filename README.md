# 🎨 PaintPro Inventory Management System

Welcome to **PaintPro IMS**, a premium, commercial-grade Inventory Management System built specifically for modern paint retailers, hardware stores, and wholesale distributors. 

Built on Python, Streamlit, and MySQL, PaintPro combines state-of-the-art UI/UX (featuring glassmorphism, dynamic animations, and dark mode) with robust business logic.


## ✨ Features

- **🔐 Role-Based Access Control (RBAC):** Admin, Manager, and Employee roles with specific module access boundaries and encrypted `bcrypt` passwords.
- **📦 Advanced Inventory & POS:** Manage products, categories, and brands. Complete point-of-sale functionality with dynamic stock deduction.
- **🎨 Visual Paint Grid:** Products are displayed as color-coded swatches utilizing their specific HEX codes.
- **🧠 AI Predictive Restocking:** Analyzes 30-day sales velocity to predict out-of-stock dates and automatically suggests reorder quantities.
- **🏷️ Barcode & QR Integration:** Auto-generates Code128 Barcodes and QR Codes for physical bin labeling and fast scanning.
- **📄 PDF Invoicing:** Generates highly professional, printable A4 PDF invoices for sales utilizing `fpdf2`.
- **🔔 Dynamic Notification Center:** Intelligent system alerts for low stock, overdue invoices, and delayed purchase orders.
- **📥 Export System:** 1-Click secure CSV database backups for accounting synchronization (QuickBooks/Tally).
- **📊 Business Analytics:** Visual dashboard utilizing Streamlit charts for Revenue, COGS, Gross Margins, and Stock Valuations.


## 🛠️ Architecture

painting/
├── app.py                      # Main application entry point & router
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (DB Config)
├── assets/
│   └── css/main.css            # Premium design system & CSS overrides
├── config/
│   └── constants.py            # RBAC rules, ENUMs, Dropdown lists
├── database/
│   ├── connection.py           # MySQL Connection pooling & execution engine
│   └── migrations.py           # SQL DDL schemas and database seed scripts
├── models/
│   ├── auth.py                 # Core authentication methods
│   ├── product.py              # Product/Inventory database logic
│   ├── purchase.py             # Atomic SQL transactions for Purchasing
│   └── sale.py                 # Atomic SQL transactions for POS/Sales
├── utils/
│   ├── auth.py                 # Session state and bcrypt hashing
│   ├── validators.py           # Input sanitization and regex validations
│   ├── formatting.py           # Currency, Date, and Slugify formatters
│   ├── pdf_generator.py        # PDF Engine for invoices
│   ├── barcode_gen.py          # In-memory QR & Barcode generation
│   └── notifications.py        # Dynamic system alerts engine
├── components/
│   ├── global_search.py        # Cross-table search modal
│   └── color_preview.py        # Paint hex swatch UI component
├── pages/                      # Application UI Views
│   ├── dashboard.py
│   ├── analytics.py
│   ├── inventory.py
│   ├── ... (sales, purchases, reports, etc.)
└── tests/
    └── test_core.py            # Pytest automated test suite
```


## 🚀 Installation & Deployment

### 1. Prerequisites
- **Python 3.10+**
- **MySQL Server 8.0+**

### 2. Setup Environment
Clone the repository and install the required dependencies:
```bash
git clone https://github.com/your-org/paintpro-ims.git
cd paintpro-ims
pip install -r requirements.txt
```

### 3. Database Configuration
Create a `.env` file in the root directory and add your MySQL credentials:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=paint_inventory
```

### 4. Database Migration
Run the automated migration script to build the SQL schema, triggers, and seed the default Demo data:
```bash
python database/migrations.py
```

### 5. Run the Application
Launch the application locally using Streamlit:
```bash
streamlit run app.py
```
*The app will automatically open in your default browser at `http://localhost:8501`.*


## 🧪 Testing

To verify the core business logic (hashing, validators, utils), simply run the test suite:
```bash
pytest tests/test_core.py -v
```


## 🔒 Security Notes
- Database transactions for Sales and Purchases are atomic (all-or-nothing) to prevent fragmented data.
- Passwords are strictly hashed with `bcrypt` (Cost Factor: 12).
- SQL Injection protection is inherently handled via parameterized queries in `mysql.connector`. 


