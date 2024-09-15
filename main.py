from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import User
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Firebase
cred = credentials.Certificate('firebase_config.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return User(id=user_id, email=user_data['email'], username=user_data['username'], role=user_data['role'])
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_doc = db.collection('users').where('email', '==', email).limit(1).get()
        if user_doc:
            user_data = user_doc[0].to_dict()
            if check_password_hash(user_data['password'], password):
                user = User(id=user_doc[0].id, email=user_data['email'], username=user_data['username'], role=user_data['role'])
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
        password = request.form.get('password')
        
        # Check if the email already exists
        existing_user = db.collection('users').where('email', '==', email).limit(1).get()
        if existing_user:
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))
        
        # Create a new user
        new_user = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'role': 'admin' if email == 'kodigolekua@gmail.com' else 'user'
        }
        
        # Add the user to the database
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

@app.route('/divisions')
def divisions():
    divisions = db.collection('divisions').order_by('name').get()
    return render_template('divisions.html', divisions=divisions)

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
    
    users = db.collection('users').get()
    user_list = [User(id=user.id, email=user.to_dict()['email'], username=user.to_dict()['username'], role=user.to_dict()['role']) for user in users]
    return render_template('admin.html', users=user_list)

@app.route('/admin/edit_user/<string:user_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_user(user_id):
    if not current_user.is_admin():
        flash('You do not have permission to edit users.', 'error')
        return redirect(url_for('index'))
    
    user_doc = db.collection('users').document(user_id).get()
    if not user_doc.exists:
        flash('User not found.', 'error')
        return redirect(url_for('admin'))
    
    user_data = user_doc.to_dict()
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        
        db.collection('users').document(user_id).update({
            'username': username,
            'email': email,
            'role': role
        })
        
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin'))
    
    return render_template('edit_user.html', user=user_data)

@app.route('/admin/delete_user/<string:user_id>')
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin():
        flash('You do not have permission to delete users.', 'error')
        return redirect(url_for('index'))
    
    db.collection('users').document(user_id).delete()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/manage_news', methods=['GET', 'POST'])
@login_required
def admin_manage_news():
    if not current_user.is_admin():
        flash('You do not have permission to manage news.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        date = datetime.now()

        new_news = {
            'title': title,
            'content': content,
            'date': date
        }
        db.collection('news').add(new_news)
        flash('News item added successfully.', 'success')
        return redirect(url_for('admin_manage_news'))

    news_items = db.collection('news').order_by('date', direction=firestore.Query.DESCENDING).get()
    return render_template('admin_manage_news.html', news_items=news_items)

@app.route('/admin/edit_news/<string:news_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_news(news_id):
    if not current_user.is_admin():
        flash('You do not have permission to edit news.', 'error')
        return redirect(url_for('index'))

    news_doc = db.collection('news').document(news_id).get()
    if not news_doc.exists:
        flash('News item not found.', 'error')
        return redirect(url_for('admin_manage_news'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')

        db.collection('news').document(news_id).update({
            'title': title,
            'content': content
        })
        flash('News item updated successfully.', 'success')
        return redirect(url_for('admin_manage_news'))

    return render_template('admin_edit_news.html', news=news_doc.to_dict())

@app.route('/admin/delete_news/<string:news_id>')
@login_required
def admin_delete_news(news_id):
    if not current_user.is_admin():
        flash('You do not have permission to delete news.', 'error')
        return redirect(url_for('index'))

    db.collection('news').document(news_id).delete()
    flash('News item deleted successfully.', 'success')
    return redirect(url_for('admin_manage_news'))

@app.route('/admin/manage_divisions', methods=['GET', 'POST'])
@login_required
def admin_manage_divisions():
    if not current_user.is_admin():
        flash('You do not have permission to manage divisions.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name')
        champion = request.form.get('champion')
        top_contenders = request.form.get('top_contenders').split(',')

        new_division = {
            'name': name,
            'champion': champion,
            'top_contenders': top_contenders
        }
        db.collection('divisions').add(new_division)
        flash('Division added successfully.', 'success')
        return redirect(url_for('admin_manage_divisions'))

    divisions = db.collection('divisions').order_by('name').get()
    return render_template('admin_manage_divisions.html', divisions=divisions)

@app.route('/admin/edit_division/<string:division_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_division(division_id):
    if not current_user.is_admin():
        flash('You do not have permission to edit divisions.', 'error')
        return redirect(url_for('index'))

    division_doc = db.collection('divisions').document(division_id).get()
    if not division_doc.exists:
        flash('Division not found.', 'error')
        return redirect(url_for('admin_manage_divisions'))

    if request.method == 'POST':
        name = request.form.get('name')
        champion = request.form.get('champion')
        top_contenders = request.form.get('top_contenders').split(',')

        db.collection('divisions').document(division_id).update({
            'name': name,
            'champion': champion,
            'top_contenders': top_contenders
        })
        flash('Division updated successfully.', 'success')
        return redirect(url_for('admin_manage_divisions'))

    return render_template('admin_edit_division.html', division=division_doc.to_dict())

@app.route('/admin/delete_division/<string:division_id>')
@login_required
def admin_delete_division(division_id):
    if not current_user.is_admin():
        flash('You do not have permission to delete divisions.', 'error')
        return redirect(url_for('index'))

    db.collection('divisions').document(division_id).delete()
    flash('Division deleted successfully.', 'success')
    return redirect(url_for('admin_manage_divisions'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
