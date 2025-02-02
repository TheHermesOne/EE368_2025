from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "Login Page"

@app.route('/SignUp')
def home():
    return "Sgin Up Page"

@app.route('/ResetPassword')
def home():
    return "Reset Password Page"

@app.route('/Success')
def home():
    return "Sucess Page"

if __name__ == "__main__":
    app.run(debug=True)