from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for
import bcrypt
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
mongo_client = MongoClient("mongo", 27017)
db = mongo_client["cse312_Group_Project"]
users_collection = db['users']

@app.route('/static/<filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return render_template('index.html')

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