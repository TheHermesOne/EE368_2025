from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from OauthApp import app

app.secret_key = 'gnbgjnbvgjnvfynbvfyjnvfkmnvghkm;09654'

BACKEND_URL = "http://127.0.0.1:5000"  # Ensure your backend runs on this URL


@app.route('/')
def index():
    if 'userEmail' in session:
        return redirect(url_for('welcomepage'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('mail')
        password = request.form.get('psw')

        response = requests.post(f"{BACKEND_URL}/api/login", json={"email": email, "password": password})
        data = response.json()
        print(data)
        if response.status_code == 200:
            session['userEmail'] = email
            session['UserData'] = data
            print(session['UserData'])
            return redirect(url_for('welcomepage'))
        else:
            flash(data.get("message", "Login failed"))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('psw')
        print(email, password, first_name, last_name)
        # Call backend to create a new user
        response = requests.post(f"{BACKEND_URL}/api/signup", json={
            'first_name': first_name,
            "last_name": last_name,
            "email": email,
            "password": password
        })

        data = response.json()
        if response.status_code == 201:
            flash("Signup successful! Please log in.")
            return redirect(url_for('login'))
        else:
            flash(data.get("message", "Signup failed"))

    return render_template('register.html')


@app.route('/welcomepage/')
def welcomepage():
    return render_template('welcomepage.html', )# This is Broken but it works for the time being


@app.route('/logout')
def logout():
    session.pop('userEmail', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
