from flask import Flask, render_template, request, redirect, url_for,session

app = Flask(__name__)
app.secret_key='gnbgjnbvgjnvfynbvfyjnvfkmnvghkm;09654'
@app.route('/')
def index():
    if 'userEmail' in session:
        return redirect(url_for('welcomepage', UserEmail=session["userEmail"]))
    return redirect(url_for('login'))
@app.route('/login', methods= ['GET','POST'])
def login():
    if request.method == 'POST':
        if 'login' in request.form:
            session['userEmail'] = request.form.get('mail')
            session['password'] = request.form.get('psw')
            return redirect(url_for('welcomepage',UserEmail=session['userEmail']))
    return render_template('login.html')
@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/changepassword')
def changepassword():
    return render_template('changepassword.html')
@app.route('/welcomepage/<UserEmail>')
def welcomepage(UserEmail = None):
    return render_template('welcomepage.html',user=UserEmail)

@app.route('/logout')
def logout():
    session.pop('userEmail',None)
    session.pop('password',None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)