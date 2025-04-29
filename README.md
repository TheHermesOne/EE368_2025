# EE368_2025
Softie Project

To Run:

In the extracted directory run the following command to build the project as a package
```
pip install -e .
```

To run the flask app use

```
flask --app .\OauthApp\ --run
```

To link the My SQL to your personal application you must go into the INIT.py file and write your username and password for your My SQL account. Then in your command prompt of SQL type the following commands.

```
CREATE DATABASE flask_db;
```
```
USE flask_db;
```
```
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    Oauth_token VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
To successfully use this application you must have an email to register an account or a Google/Github to log in with a third party provider.
