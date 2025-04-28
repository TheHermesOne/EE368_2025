from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from OauthApp import app
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import WebApplicationClient
import json
import os
from OauthApp import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL, REDIRECT_URI
from authlib.integrations.flask_client import OAuth
import re

client = WebApplicationClient(GOOGLE_CLIENT_ID)

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

def validate_password(password):
    if len(password) < 12:
        return False, "Password must be at least 12 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""

@app.route('/')
def index():
    user_data = session.get('UserData')
    if user_data and user_data.get('first_name'):
        return redirect(url_for('welcomepage', User=user_data['first_name']))
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


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/login/google")
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=REDIRECT_URI,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/callback/google")
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=REDIRECT_URI,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    user_info = userinfo_response.json()

    # Store user info in session
    requests.post(f"{BACKEND_URL}/api/oauth_login", json={
        "email": user_info["email"],
        "first_name": user_info.get("given_name", ""),
        "last_name": user_info.get("family_name", ""),
        "oauth_token": token_response.json()['access_token']

    })
    backend_response = requests.post(f"{BACKEND_URL}/api/get_user_by_email", json={
        "email": user_info["email"],
        "password": ""  # OAuth users don't have password, maybe modify /api/login to allow token auth
    })
    if backend_response.status_code == 200:
        session['UserData'] = backend_response.json()
    else:
        session['UserData'] = {
            "email": user_info["email"],
            "first_name": user_info.get("given_name", ""),
            "last_name": user_info.get("family_name", ""),
            "userID": user_info.get("sub")
        }

    return redirect(url_for('welcomepage', User=session['UserData']['first_name']))
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

    # Still post to oauth_login to register/update user
    requests.post(f"{BACKEND_URL}/api/oauth_login", json={
        "email": user_info["email"],
        "first_name": user_info.get("login", ""),  # using GitHub username as first name
        "last_name": "",
        "oauth_token": token['access_token']
    })

    # ⚡ NEW: fetch user info from YOUR backend
    backend_response = requests.post(f"{BACKEND_URL}/api/get_user_by_email", json={
        "email": user_info["email"]
    })

    if backend_response.status_code == 200:
        session['UserData'] = backend_response.json()
    else:
        # fallback if backend fails
        session['UserData'] = {
            "email": user_info["email"],
            "first_name": user_info.get("name", ""),
            "last_name": "",
            "userID": user_info["id"],
            "login": user_info.get("login", "")
        }

    return redirect(url_for('welcomepage', User=session['UserData']['first_name']))

@app.route('/signup', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('fname')
        last_name = request.form.get('lname')
        email = request.form.get('mail')
        password = request.form.get('psw')
        confirm_password = request.form.get('cpsw')

        # valid password check
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('register'))

        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message)
            return redirect(url_for('register'))

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
    return render_template('welcomepage.html',user_data = session['UserData'] )


@app.route('/logout')
def logout():
    user_data = session.get('UserData')
    if user_data:
        # Send a request to the backend to clear the user's token
        try:
            requests.post(f"{BACKEND_URL}/api/logout", json={"email": user_data.get("email")})
        except Exception as e:
            print(f"Error contacting backend during logout: {e}")

    session.clear()
    return redirect(url_for('index'))


@app.route('/changePassword', methods=['GET', 'POST'])
def changePassword():
    if request.method == 'POST':
        email = request.form.get('mail')
        password = request.form.get('newpsw')
        confirm_password = request.form.get('cpsw')

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for('changePassword'))

        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message)
            return redirect(url_for('changePassword'))

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



@app.route('/newnames', methods=['GET', 'POST'])
def newnames():
    if request.method == 'POST':
        email = request.form.get('mail')
        fname = request.form.get('newfname')
        lname = request.form.get('newlname')
        response = requests.post(f"{BACKEND_URL}/api/newnames", json={
            "email": email,
            "fname": fname,
            "lname": lname
        })
        data = response.json()
        print(response.status_code)
        if response.status_code == 200:
            if 'UserData' in session:
                session['UserData']['first_name'] = fname
                session['UserData']['last_name'] = lname

            flash("Name changes successful!")
            return redirect(url_for('welcomepage', User=fname))
        else:
            flash(data.get("message", "Name change failed"))
    return render_template('newnames.html')


if __name__ == "__main__":
    app.run(debug=True)
