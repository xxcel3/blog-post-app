from flask import Flask, render_template, send_from_directory, request, jsonify, make_response 
from flask_bcrypt import Bcrypt
from pymongo import PyMongo
import uuid
import datetime



app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/users'

mongo = PyMongo(app)
bcrypt = Bcrypt(app)


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    data = request.get_json()
    user = users.find_one({'username': data['username']})

    if not user or not bcrypt.check_password_hash(user['password'], data['password']):
        return make_response('Login failed', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    # Generate authentication token
    token = str(uuid.uuid4())
    users.update_one({'id': user['id']}, {'$set': {'auth_token': token}})

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5050)