from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
@app.route('/')
def index():
    return redirect(url_for('login'))
@app.route('/login', methods= ['POST'])
def login():
    if request.method == 'POST':
        if 'login' in request.form:
            username = request.form.get('uname')
            password = request.form.get('psw')
            app.logger.info(f"Username: {username}, Password: {password}")
    return render_template('login.html')
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/changepassword')
def changepassword():
    return render_template('changepassword.html')

@app.route('/welcomepage')
def welcome():
    return render_template('welcomepage.html')

if __name__ == "__main__":
    app.run(debug=True)