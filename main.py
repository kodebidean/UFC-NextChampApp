import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize Firebase
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email, username, role='user'):
        self.id = id
        self.email = email
        self.username = username
        self.role = role

    def is_admin(self):
        return self.role == 'admin'

def get_divisions_data():
    try:
        df = pd.read_excel('0-UFCnextChamp-Sheet.xlsx', sheet_name=None)
        divisions = {}
        for sheet_name, sheet_data in df.items():
            # Ensure all columns are present and in the correct order
            columns = ['Nombre', 'Apodo', 'Born Date', 'Country 1', 'Country 2', 'Arte Marcial 1', 'Arte Marcial 2', 'Arte Marcial 3', 'Arte Marcial 4', 'Fuerza', 'Velocidad', 'Resistencia', 'Agilidad', 'Flexibilidad', 'Defensa', 'Ataque', 'Golpe de Poder']
            sheet_data = sheet_data.reindex(columns=columns)
            divisions[sheet_name] = sheet_data.fillna('').to_dict('records')
        return divisions
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def save_updated_divisions(updated_data):
    try:
        with pd.ExcelWriter('0-UFCnextChamp-Sheet.xlsx') as writer:
            for division, fighters in updated_data.items():
                df = pd.DataFrame(fighters)
                # Ensure columns are in the correct order
                columns = ['Nombre', 'Apodo', 'Born Date', 'Country 1', 'Country 2', 'Arte Marcial 1', 'Arte Marcial 2', 'Arte Marcial 3', 'Arte Marcial 4', 'Fuerza', 'Velocidad', 'Resistencia', 'Agilidad', 'Flexibilidad', 'Defensa', 'Ataque', 'Golpe de Poder']
                df = df.reindex(columns=columns)
                df.to_excel(writer, sheet_name=division, index=False)
        print("Excel file updated successfully.")
    except Exception as e:
        print(f"Error updating Excel file: {e}")

@login_manager.user_loader
def load_user(user_id):
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        if user_data:
            return User(
                id=user_id,
                email=user_data.get('email', ''),
                username=user_data.get('username', ''),
                role=user_data.get('role', 'user')
            )
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password') or ''
        user_doc = db.collection('users').where('email', '==', email).limit(1).get()
        if user_doc and len(user_doc) > 0:
            user_data = user_doc[0].to_dict()
            if user_data and check_password_hash(user_data.get('password', ''), password):
                user = User(id=user_doc[0].id,
                            email=user_data.get('email', ''),
                            username=user_data.get('username', ''),
                            role=user_data.get('role', 'user'))
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('admin') if user.is_admin() else url_for('index'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password') or ''
        existing_user = db.collection('users').where('email', '==', email).limit(1).get()
        if existing_user:
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))
        new_user = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'role': 'admin' if email == 'kodigolekua@gmail.com' else 'user'
        }
        db.collection('users').add(new_user)
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/divisions', methods=['GET', 'POST'])
@login_required
def divisions():
    if request.method == 'POST' and current_user.is_admin():
        updated_data = {}
        for key, value in request.form.items():
            division, index, field = key.split('-')
            if division not in updated_data:
                updated_data[division] = []
            while len(updated_data[division]) <= int(index):
                updated_data[division].append({})
            updated_data[division][int(index)][field] = value
        
        save_updated_divisions(updated_data)
        flash('Division data updated successfully.', 'success')
        return redirect(url_for('divisions'))

    divisions_data = get_divisions_data()
    if divisions_data is None:
        flash('Error fetching fighter data. Please try again later.', 'error')
        return render_template('divisions.html', divisions={})
    return render_template('divisions.html', divisions=divisions_data)

@app.route('/news')
def news():
    news_items = db.collection('news').order_by('date', direction=firestore.Query.DESCENDING).get()
    return render_template('news.html', news_items=news_items)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin():
        flash('You do not have permission to access the admin panel.', 'error')
        return redirect(url_for('index'))
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
