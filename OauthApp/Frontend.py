from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from OauthApp import app
from authlib.integrations.flask_client import OAuth



BACKEND_URL = "http://127.0.0.1:5000"  # Ensure your backend runs on this URL

oauth = OAuth(app)
github = oauth.register(
name='github',
client_id='Ov23lik1vP32ryWXacGW',
client_secret='5cda03c8137f3225e6261352ddfc86c977645611',
access_token_url='https://github.com/login/oauth/access_token',
authorize_url='https://github.com/login/oauth/authorize',
api_base_url='https://api.github.com/',
client_kwargs={'scope': 'user:email'},
)
@app.route('/')
def index():
    if 'UserData' in session and 'email' in session['UserData']:
        return redirect(url_for('welcomepage',User = session['UserData']['first_name']))
    else:
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
            session['UserData'] = data
            print(session['UserData'])
            return redirect(url_for('welcomepage',User = session['UserData']['first_name']))
        else:
            flash(data.get("message", "Login failed"))

    return render_template('login.html')

@app.route('/githubLogin')
def githublogin():
   return github.authorize_redirect(url_for('authorize', _external=True))


@app.route('/login/callback')
def authorize():
   token = github.authorize_access_token()
   resp = github.get('user', token=token)
   emailresp = github.get('user/emails', token=token)
   email = emailresp.json()
   user_info = resp.json()
   primary_email = next((e['email'] for e in email if e.get('primary')), None)
   user_info['email'] = primary_email
   session['userData'] = user_info
   return redirect(url_for('welcomepage',User = session['userData']['login']))

@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        email = request.form.get('mail')
        password = request.form.get('psw')

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


@app.route('/welcomepage/<User>')
def welcomepage(User = None):
    return render_template('welcomepage.html',user_data = session['userData'] )


@app.route('/logout')
def logout():
    session.pop('UserData', None)
    return redirect(url_for('index'))

@app.route('/changePassword', methods=['GET', 'POST'])
def changePassword():
    if request.method == 'POST':
        email = request.form.get('mail')
        password = request.form.get('newpsw')
        response = requests.post(f"{BACKEND_URL}/api/changePassword", json={
            "email": email,
            "password": password
        })
        data = response.json()
        print(response.status_code)
        if response.status_code == 200:
            flash("Password changed successfully!")
            return redirect(url_for('login'))
        else:
            flash(data.get("message", "Password change failed"))
    return render_template('forgotpw.html')

if __name__ == "__main__":
    app.run(debug=True)
