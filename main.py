from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from config import Config
from models import User

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # This is a placeholder. We'll implement user loading later.
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Placeholder for login logic
        flash('Login functionality not implemented yet.', 'info')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Placeholder for registration logic
        flash('Registration functionality not implemented yet.', 'info')
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
    # Placeholder for divisions data
    divisions = [
        {"name": "Heavyweight", "champion": "Jon Jones", "top_contenders": ["Ciryl Gane", "Stipe Miocic", "Tom Aspinall"]},
        {"name": "Light Heavyweight", "champion": "Alex Pereira", "top_contenders": ["Jamahal Hill", "Jiri Prochazka", "Magomed Ankalaev"]},
        {"name": "Middleweight", "champion": "Israel Adesanya", "top_contenders": ["Dricus Du Plessis", "Sean Strickland", "Robert Whittaker"]}
    ]
    return render_template('divisions.html', divisions=divisions)

@app.route('/news')
def news():
    # Placeholder for news data
    news_items = [
        {"id": 1, "title": "UFC 300 Announced", "date": "2024-09-15", "content": "UFC 300 set to be the biggest event in UFC history."},
        {"id": 2, "title": "New Champion Crowned", "date": "2024-09-14", "content": "Upset victory leads to new champion in the welterweight division."},
        {"id": 3, "title": "Rising Star to Debut", "date": "2024-09-13", "content": "Highly anticipated prospect set to make UFC debut next month."}
    ]
    return render_template('news.html', news_items=news_items)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
