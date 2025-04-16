from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
import os
import bcrypt
import numpy as np
from flask_cors import CORS
import pickle

app = Flask(__name__)
app.secret_key = "supersecretkey"

CORS(app)


# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['medico_db']
users_collection = db['users']

# Load model once


# Dummy symptom-to-index map (replace with your real map)
symptom_index = {
    'itching': 0,
    'skin_rash': 1,
    'nodal_skin_eruptions': 2,
    # ... add all symptoms here in the same order as training
}

# Dummy output mapping (update based on your model training)
disease_classes = [
    "Allergy", "Fungal infection", "GERD", "Chronic cholestasis",
    "Drug Reaction", "Peptic ulcer disease", "AIDS"
    # ... extend this list according to your model
]

# ---------- ROUTES ----------

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Collect form data
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

        if password != retype_pass:
            flash('Passwords do not match!')
            return render_template('register.html')

        if users_collection.find_one({"email": email}):
            flash('User already registered with this email.')
            return render_template('register.html')

        if users_collection.find_one({"username": username}):
            flash('Username already taken.')
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

        users_collection.insert_one(user_data)
        session['username'] = username
        flash('Registration successful!')
        return redirect(url_for('prediction'))

    return render_template('register.html')


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


@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if 'username' not in session:
        flash("Please login to access this page.", "warning")
        return redirect(url_for('login'))

    prediction_result = None

    if request.method == 'POST':
        # Collect symptoms
        symptoms = [
            request.form.get('symptom 1'),
            request.form.get('symptom 2'),
            request.form.get('symptom 3'),
            request.form.get('symptom 4'),
            request.form.get('symptom 5')
        ]

        # Convert to input vector
        input_vector = [0] * len(symptom_index)
        for symptom in symptoms:
            if symptom and symptom.strip() != "select":
                symptom_key = symptom.strip()
                if symptom_key in symptom_index:
                    input_vector[symptom_index[symptom_key]] = 1

        # Predict
        prediction = model.predict([np.array(input_vector)])
        predicted_disease = disease_classes[np.argmax(prediction)]
        prediction_result = f"Predicted Disease: {predicted_disease}"

    return render_template("prediction.html", prediction=prediction_result, username=session['username'])


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')


@app.route('/FAQ')
def FAQ():
    return render_template('FAQ.html')


if __name__ == '__main__':
    app.run(debug=True)
