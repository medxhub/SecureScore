#from flask import Flask, render_template, request
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required
from datetime import timedelta

import sqlite3
import numpy as np
from sklearn.linear_model import LogisticRegression
import pandas as pd




# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bjtth/bn0rDQY8FRPOYut9qhDBYg1Llm8UbONZaF'
# Set session duration to 30 minutes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

@app.before_request
def make_session_permanent():
    # Make the session permanent, meaning it lasts until the configured lifetime
    session.permanent = True


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect users to login page if not authenticated


# Translation dictionary
translations = {
    'en': {
        'title': 'SecureScore',
        'name':'Name',
        'dob':'Date of birth',
        'marital_status':'Marital Status',
        'education_level':'Education Level',
        'applicants_title': 'Loan Applicants',
        'credit_score': 'Credit Score',
        'income': 'Monthly Income',
        'debt_to_income_ratio': 'Debt-to-Income Ratio',
        'loan_amount': 'Loan Amount',
        'loan_to_value_ratio': 'Loan-to-Value Ratio',
        'employment_years': 'Years of Employment',
        'submit': 'Calculate Risk Score',
        'risk_score': 'Risk Score',
        'risk_level': 'Risk Level',
        'dashboard':'SecureScore Dashboard'
    },
    'fr': {
        'title': 'SecureScore',
        'name':'Nom',
        'dob':'Date de naissance',
        'marital_status':'Etat civil',
        'education_level':'Niveau d\'études',
        'applicants_title': 'Candidats aux prêts',
        'credit_score': 'Score de crédit',
        'income': 'Revenu mensuel',
        'debt_to_income_ratio': 'Ratio dette/revenu',
        'loan_amount': 'Montant du prêt',
        'loan_to_value_ratio': 'Ratio prêt/valeur',
        'employment_years': 'Années d\'emploi',
        'submit': 'Calculer le score de risque',
        'risk_score': 'Score de risque',
        'risk_level': 'Niveau de risque',
        'dashboard':'Tableau de bord SecureScore'
    }
}

# Dummy dataset (same as used before) for training the logistic regression model
data = pd.DataFrame({
    'credit_score': [700, 650, 600, 750, 800, 580, 610, 640, 620, 690],
    'income': [5000, 4000, 3000, 6000, 7000, 2800, 3200, 4500, 3300, 4800],
    'debt_to_income_ratio': [0.2, 0.3, 0.35, 0.25, 0.15, 0.4, 0.38, 0.28, 0.32, 0.22],
    'loan_amount': [20000, 15000, 10000, 30000, 40000, 9000, 12000, 16000, 11000, 18000],
    'loan_to_value_ratio': [0.7, 0.8, 0.9, 0.65, 0.6, 0.92, 0.88, 0.75, 0.85, 0.68],
    'employment_years': [5, 2, 1, 6, 10, 1, 3, 4, 2, 7],
    'defaulted': [0, 1, 1, 0, 0, 1, 1, 0, 1, 0]
})

# Features and target variable
X = data[['credit_score', 'income', 'debt_to_income_ratio', 'loan_amount', 'loan_to_value_ratio', 'employment_years']]
y = data['defaulted']

# Train logistic regression model
model = LogisticRegression()
model.fit(X, y)

# Function to score new applicant
def score_new_applicant(credit_score, income, debt_to_income_ratio, loan_amount, loan_to_value_ratio, employment_years):
    applicant_data = np.array([credit_score, income, debt_to_income_ratio, loan_amount, loan_to_value_ratio, employment_years]).reshape(1, -1)
    risk_score = model.predict_proba(applicant_data)[0][1]
    
    # Classify based on risk score thresholds
    if risk_score < 0.3:
        risk_level = 'Low Risk'
    elif 0.3 <= risk_score <= 0.6:
        risk_level = 'Moderate Risk'
    else:
        risk_level = 'High Risk'
    
    return risk_score, risk_level

# Database connection function
def connect_db():
    return sqlite3.connect('database.db')

# Check if the user is over 18 years old (GDPR compliant age restriction)
def is_over_18(dob):
    birth_date = datetime.strptime(dob, '%Y-%m-%d')
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age >= 18

# Ensure the user table exists for login management
def init_user_db():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Call this to initialize the user table
init_user_db()


# Flask-Login user class
class User(UserMixin):
    def __init__(self, id, username, password, role):
        self.id = id
        self.username = username
        self.password = password
        self.role = role

# Load user from the database by user ID
@login_manager.user_loader
def load_user(user_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(id=user[0], username=user[1], password=user[2], role=user[3])
    return None

# Register route (optional if you need a registration page)
@app.route('/register', methods=['GET', 'POST'])
def register():
    return "Registration is disabled."
#    if request.method == 'POST':
#        username = request.form['username']
#        password = request.form['password']
#        hashed_password = generate_password_hash(password)

#        # Store the new user in the database
#        conn = connect_db()
#        c = conn.cursor()
#        try:
#            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
#            conn.commit()
#            flash("User registered successfully!", "success")
#            return redirect(url_for('login'))
#        except sqlite3.IntegrityError:
#            flash("Username already exists!", "error")
#        finally:
#            conn.close()
#    return render_template('register.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Get language preference from URL parameters (default is 'en')
    lang = request.args.get('lang', 'en')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query the user from the database
        conn = connect_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            login_user(User(id=user[0], username=user[1], password=user[2],role=user[3]))
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "error")

    return render_template('login.html',translations=translations[lang],lang=lang)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # Clear all session data
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Define the homepage route with language support
#@app.route('/', methods=['GET'])
#@login_required
#def index():
#    # Get language preference from URL parameters (default is 'en')
#    lang = request.args.get('lang', 'en')
    
#    # Pass the appropriate translations to the template
#    return render_template('dashboard.html', translations=translations[lang], lang=lang)

@app.route('/simulation', methods=['GET'])
@login_required
def simulation():
    # Get language preference from URL parameters (default is 'en')
    lang = request.args.get('lang', 'en')
    
    # Pass the appropriate translations to the template
    return render_template('simulation.html', translations=translations[lang], lang=lang)


# Define the route to process the form
@app.route('/score', methods=['POST'])
@login_required
def score():
    # Get language preference from the hidden form field
    lang = request.form['lang']
    # Get data from form
    name = request.form['name']
    dob = request.form['dob']
    marital_status = request.form['marital_status']
    education_level = request.form['education_level']
    credit_score = float(request.form['credit_score'])
    income = float(request.form['income'])
    debt_to_income_ratio = float(request.form['debt_to_income_ratio'])
    loan_amount = float(request.form['loan_amount'])
    loan_to_value_ratio = float(request.form['loan_to_value_ratio'])
    employment_years = int(request.form['employment_years'])

    # Score the applicant
    risk_score, risk_level = score_new_applicant(credit_score, income, debt_to_income_ratio, loan_amount, loan_to_value_ratio, employment_years)

    # Store the data in the database
    conn = connect_db()
    c = conn.cursor()
    c.execute('''INSERT INTO applicants
        (name, dob, marital_status, education_level, credit_score, income, debt_to_income_ratio, loan_amount, loan_to_value_ratio, employment_years, risk_score, risk_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (name, dob, marital_status, education_level, credit_score, income, debt_to_income_ratio, loan_amount, loan_to_value_ratio, employment_years, risk_score, risk_level))

    conn.commit()
    conn.close()

    # Return the result to the user with translations
    return render_template('simulation.html', translations=translations[lang], lang=lang, risk_score=round(risk_score, 2), risk_level=risk_level)

# New route to list loan applicants
@app.route('/applicants', methods=['GET'])
@login_required
def list_applicants():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM applicants')
    applicants = c.fetchall()
    conn.close()

    # Get language preference from URL parameters (default is 'en')
    lang = request.args.get('lang', 'en')

    # Pass the appropriate translations to the template
    return render_template('applicants.html', translations=translations[lang], lang=lang,applicants=applicants)


# Endpoint to delete user data (GDPR compliance: Right to be forgotten)
@app.route('/delete_user/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    #user_id = request.form['user_id']

    conn = connect_db()
    c = conn.cursor()
    c.execute('DELETE FROM applicants WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    return "User data deleted."

# Endpoint to export user data (GDPR compliance: Right to data portability)
@app.route('/export_data/<int:user_id>', methods=['GET'])
@login_required
def export_data(user_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM applicants WHERE id = ?', (user_id,))
    data = c.fetchone()
    conn.close()

    if data:
        user_data = {
            'name': data[1],
            'dob': data[2],
            'marital_status': data[3],
            'education_level': data[4],
            'credit_score': data[5],
            'income': data[6],
            'debt_to_income_ratio': data[7],
            'loan_amount': data[8],
            'loan_to_value_ratio': data[9],
            'employment_years': data[10],
            'risk_score': data[11],
            'risk_level': data[12],
        }
        return user_data  # Flask will return this as a JSON response

    return "User not found", 404

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def manage_users():
    # Check if the logged-in user is an admin
    if current_user.role != 'admin':
        flash("You do not have permission to view this page.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Handle the form to create a new user
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Insert the new user into the database
        conn = connect_db()
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))
            conn.commit()
            flash("User created successfully!", "success")
        except sqlite3.IntegrityError:
            flash("Username already exists!", "error")
        finally:
            conn.close()

    # Retrieve all users from the database for display
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT id, username, role FROM users')
    users = c.fetchall()
    conn.close()

    return render_template('manage_users.html', users=users)

@app.route('/')
@login_required
def index():
    conn = connect_db()
    c = conn.cursor()

    # Query for total number of customers
    c.execute('SELECT COUNT(*) FROM applicants')
    total_customers = c.fetchone()[0]

    # Query for total number of loans applied
    c.execute('SELECT SUM(loan_amount) FROM applicants')
    total_loans = c.fetchone()[0]

    # Query for total approved loans
    c.execute('SELECT COUNT(*) FROM loans WHERE status = "approved"')
    approved_loans = c.fetchone()[0]

    # Query for pending loans
    c.execute('SELECT COUNT(*) FROM loans WHERE status = "pending"')
    pending_loans = c.fetchone()[0]

    # Closing the connection
    conn.close()
    lang = request.args.get('lang', 'en')

    return render_template(
        'dashboard.html',
        total_customers=total_customers,
        total_loans=total_loans,
        approved_loans=approved_loans,
        pending_loans=pending_loans,
        translations=translations[lang], lang=lang
    )


# Run the app
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
