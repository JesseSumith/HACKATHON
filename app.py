from flask import Flask, render_template, request, redirect, url_for, session, flash
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
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        username = request.form.get('username')
        contact = request.form.get('contact')
        birthdate = request.form.get('birthdate')
        gender = request.form.get('gender')
        age = request.form.get('userAge')
        email = request.form.get('userEmail')
        password = request.form.get('userPass')
        retype_pass = request.form.get('retypePass')

        print("Form Data:", fname, lname, username, email)

        if password != retype_pass:
            flash('Passwords do not match!')
            print("Password mismatch")
            return render_template('register.html')

        if users_collection.find_one({"email": email}):
            flash('User already registered with this email.')
            print("Duplicate email")
            return render_template('register.html')

        if users_collection.find_one({"username": username}):
            flash('Username already taken.')
            print("Duplicate username")
            return render_template('register.html')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user_data = {
            "fname": fname,
            "lname": lname,
            "username": username,
            "contact": contact,
            "birthdate": birthdate,
            "gender": gender,
            "age": age,
            "email": email,
            "password": hashed_password
        }

        result = users_collection.insert_one(user_data)
        print("Inserted user ID:", result.inserted_id)

        session['username'] = username
        flash('Registration successful!')
        return redirect(url_for('prediction'))

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
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for('prediction'))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# PREDICTION PAGE
@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if 'username' not in session:
        flash("Please login to access this page.", "warning")
        return redirect(url_for('login'))

    username = session['username']
    return render_template('prediction.html', username=username)

# LOGOUT
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

#chatbot
@app.route('/chatbot')
def chatbot():
    
    return render_template('chatbot.html')

#FAQ
@app.route('/FAQ')
def FAQ():

    return render_template('FAQ.html')
# Run the app
if __name__ == '__main__':
    app.run(debug=True)






