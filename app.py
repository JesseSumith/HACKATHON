from flask import Flask, render_template, request, redirect, url_for,session, flash 
from pymongo import MongoClient
import os
import bcrypt

app = Flask(__name__)

app.secret_key = "supersecretkey"

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")  # Use your Atlas URI if using cloud
db = client['medico_db']
users_collection = db['users']

# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')  # This should be inside the templates/ folder

# REGISTER PAGE
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']

        if users_collection.find_one({'username': username}):
            return 'User already exists. Try logging in.'

        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())

        users_collection.insert_one({
            'username': username,
            'password': hashed_password
        })

        return 'Registration successful! <a href="/login">Login here</a>'

    return render_template('register.html')


# LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']

        user = users_collection.find_one({'username': username})

        if user and bcrypt.checkpw(raw_password.encode('utf-8'), user['password']):
            session['username'] = username
            flash(f"Welcome back, {username}!", "success")  # ✅ flash message
            return redirect(url_for('prediction'))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/prediction')
def prediction():
    if 'username' not in session:
        flash("Please login to access this page.", "warning")
        return redirect(url_for('login'))
    
    username = session['username']
    return render_template('prediction.html', username=username)


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
