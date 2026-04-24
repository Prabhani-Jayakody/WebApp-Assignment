# 💰 ExpenseWise - Personal Finance Management Application

A comprehensive web application for tracking income and expenses, categorizing spending, and generating insightful financial reports. Built with Django and Bootstrap 5.

## 📋 Project Information

-   **Course:** DA3331 - Business Application Development
-   **Group:** Group 12
-   **Topic:** Expense Tracking Application
-   **Submission Date:** 24th April 2025

## ✨ Features

### Core Features

-   ✅ **User Authentication** - Register, login, logout with profile management
-   ✅ **Dashboard** - Income, expenses, balance, savings rate, and monthly comparison
-   ✅ **Transaction Management** - Add, edit, delete transactions with payment methods
-   ✅ **Recurring Transactions** - Set regular bills as recurring
-   ✅ **Category Organization** - Health, Bills, Shopping, Food, Transport, Entertainment, Rent, Salary
-   ✅ **Payment Methods** - Cash, Card, Bank Transfer, Digital Wallet, Loan/Credit
-   ✅ **Transaction List** - Search, filter by type, payment method, and date
-   ✅ **CSV Export** - Export filtered transactions to CSV format
-   ✅ **Profile Page** - Update personal info, phone, address, bio, and profile picture

### Advanced Features

-   ✅ **Smart Insights Dashboard** - Top expenses, savings rate, daily average spending
-   ✅ **Expense Distribution Chart** - Visual breakdown by category
-   ✅ **Monthly Trend Chart** - 6-month income vs expenses comparison
-   ✅ **Category Breakdown** - Progress bars with percentages
-   ✅ **Payment Method Analysis** - Track spending by payment type
-   ✅ **Quick Date Filters** - Today, This Week, This Month, Last Month, Reset
-   ✅ **Key Metrics Cards** - Total Income, Expenses, Net Savings, Savings Rate
-   ✅ **Recent Activity Feed** - Latest transactions on add page
-   ✅ **This Month's Summary** - Monthly totals with expense ratio
-   ✅ **Savings Tips** - Personalized money-saving recommendations
-   ✅ **Responsive Design** - Works on desktop, tablet, and mobile
-   ✅ **Modern UI** - Gradient cards, smooth animations, glass morphism

## 🛠️ Technology Stack

| Technology      | Purpose                     |
|-----------------|-----------------------------|
| **Django 6.0**  | Backend web framework       |
| **SQLite3**     | Database                    |
| **Bootstrap 5** | Frontend CSS framework      |
| **Chart.js**    | Interactive doughnut charts |
| **HTML5/CSS3**  | Structure and styling       |
| **Git/GitHub**  | Version control             |

## 🚀 Installation & Setup

### Prerequisites

-   Python 3.8 or higher
-   Git

### Step 1: Clone the Repository

`git clone https://github.com/Prabhani-Jayakody/WebApp-Assignment.git`

`cd WebApp-Assignment`

### Step 2: Create Virtual Environment

windows: `python -m venv venv`

`venv\Scripts\activate\`

Mac/Linux: `python -m venv`

`venv source venv/bin/activate\`

### Step 3: Install Dependencies

`pip install -r requirements.txt`

### Step 4: Run Migrations

`python manage.py makemigrations` `python manage.py migrate`

### Step 5: Create Superuser (Admin)

`python manage.py createsuperuser`

### Step 6: Run the Application

`python manage.py runserver`

### Step 7: Access the Application

-   Main App: <http://127.0.0.1:8000/>

-   Admin Panel: <http://127.0.0.1:8000/admin/>

## 📱 How to Use

### 1. Register an Account

-   Click "Register" on the login page

-   Fill in username, email, and password

-   Submit to create your account

### 2. Add Transactions

-   Click "Add" in the navigation bar

-   Select transaction type (Income/Expense)

-   Enter amount, category, description, and date

-   Click "Save Transaction"

### 3. View Dashboard

-   See real-time totals for income, expenses, and balance

-   View recent transactions

-   Quick access to edit or delete transactions

### 4. Manage Transactions

-   Go to the "Transactions" page

-   Search by category or description

-   Filter by type (Income/Expense)

-   Filter by specific date

-   Export filtered data to CSV

### 5. Generate Reports

-   Go to the "Reports" page

-   Select date range (optional)

-   View interactive doughnut chart

-   See expense breakdown by category

-   Get smart spending insights

## 📊 Database Schema

### User Model (Django Built-in)

| Feild        | Type       | Description          |
|--------------|------------|----------------------|
| **username** | CharField  | Unique username      |
| **email**    | EmailField | User's email address |
| **password** | CharField  | Hashed password      |

### Transaction Model

| Feild           | Type         | Description          |
|-----------------|--------------|----------------------|
| **user**        | ForeignKey   | Links to User model  |
| **amount**      | DecimalField | Transaction amount   |
| **type**        | CharField    | Income or Expense    |
| **category**    | CharField    | Transaction Category |
| **description** | TextField    | Optional notes       |
| **date**        | DateField    | Transaction date     |

## 🎨 UI Features

-   Glass Morphism Navbar - Modern frosted glass effect

-   Gradient Cards - Beautiful color-coded stat cards

    Income: Golden Amber gradient

    Expenses: Rose Red gradient

    Balance: Royal Blue gradient

-   Interactive Doughnut Chart - Visual expense distribution

-   Animated Progress Bars - Smooth loading animations

-   Responsive Tables - Hover effects and scaling

-   Mobile Friendly - Optimized for all screen sizes

## 🔗 Links

GitHub Repository: <https://github.com/Prabhani-Jayakody/WebApp-Assignment>

## 📈 Commit Statistics

Total Commits: 50+

Repository: Public

## 👥 Team Members & Contributions

| Member | Contribution |
|------------------------|------------------------------------------------|
| **Savindi** | Expense & Income Management – Implemented Transaction and Category models, add/edit/delete/list transaction views, transaction forms, URL routes, Bootstrap templates and added default expense categories. |
| **Kalpana** | User Registration: Users can create a new account with username, email and password, User Login: Users can log in securely with error handling and password toggle, User Logout: Logs out the user and redirects to login page, User Profile: Displays user details, accessible only when logged in, Session Management: Restricts pages from unauthorized users automatically |
| **Prabhani** | Creating profile model and home page, Adding advanced features to user authentication system Updating transaction system, Adding features to dashboard page and report page, UI/UX design, Fixing bugs and redirecting errors |
| **Senani** | UI/UX design, Bootstrap styling, responsive layout, navigation bar, dashboard cards, reports page with doughnut chart, search & filter functionality, CSV export, date range filter, README documentation. |
