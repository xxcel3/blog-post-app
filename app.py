# <<<<<<< HEAD
from flask import Flask, render_template, send_from_directory, request, jsonify, make_response, redirect, url_for
# from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import uuid
import bcrypt
import datetime


# =======
# from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for
# import bcrypt
# from pymongo import MongoClient
# >>>>>>> 21249fd1dcb9d47421bbb0e99b2958b795e1a4db

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/users'
mongo_client = MongoClient("mongo", 27017)
db = mongo_client["cse312_Group_Project"]
users_collection = db['users']

# mongo = PyMongo(app)
# bcrypt = Bcrypt(app)
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username_reg')
    password = request.form.get('password_reg')
    confirm_password = request.form.get('password_reg_confirm')

    if not (username and password and confirm_password):
        return jsonify({'error': 'Please enter all fields'}), 400
    
    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match'}), 400
    
    if users_collection.find_one({'username': username}):
        return jsonify({'error': 'Username taken'}), 400

    # salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt).decode()

    #insert 
    users_collection.insert_one({'username': username, 'password': hashed_password})

    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username_login')
    password = request.form.get('password_login')

    if not (username and password):
        return jsonify({'error': 'BOTH Password and Username Needed'}), 400
    # users = mongo.db.users
    # data = request.get_json()
    user = users_collection.find_one({'username': username})

    if not user or not bcrypt.checkpw(password.encode(), user['password'].encode()):
        return jsonify({'error': 'Invalid username or password'}), 401

    # Generate authentication token
    token = str(uuid.uuid4())
    users_collection.update_one({'username': username}, {'$set': {'auth_token': token}})

    # Set authentication token as HttpOnly cookie
    response = make_response(jsonify({'message': 'Login successful'}))
    response.set_cookie('auth_token', token, httponly=True, expires=datetime.datetime.now() + datetime.timedelta(hours=1))
    return response

    

@app.route('/static/<filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return render_template('index.html')


'''
@app.route('/login', methods=['POST'])
def login():
    # put authentication code for login

@app.route('/logout')
def logout():
    pass
'''

# needs to be 8080
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8080)