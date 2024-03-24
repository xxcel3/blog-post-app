# <<<<<<< HEAD
from flask import Flask, render_template, send_from_directory, request, jsonify, make_response, redirect, url_for
# from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import uuid
import json
import html
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

post1_chat_collection = db["post1_chat"] #we need to find a way to create unique chat collections per unique posts

post_collection = db["posts"] #every post should keep track of user who posted and time of post creation ,maybe number of current likes(might have to use ajax to update this)

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
    
    response.headers['X-Content-Type-Options'] = 'nosniff'

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

# Where we get messages from DB
@app.route('/id/chat-message', methods=['GET','POST'])
def getMessages():
    if request.method == 'GET':    
        #all the messages from the chat collection of the DB
        allMessages = post1_chat_collection.find({}) #later can find chat message for specified post

        chats = []
        for message in allMessages:
            chats.append({"message": message["message"], "username": message["username"], "id": message["id"]}) 

        allMessagesJ = json.dumps(chats)
        response = make_response(allMessagesJ)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    elif request.method == 'POST':
        id = str(uuid.uuid4())
        authToken = request.cookies.get("auth_token")
        userInfo = list(users_collection.find({"auth_token": f"{authToken}"}))
        
        currAuthUser = userInfo[0]["username"]

        data = request.json
        message = html.escape(data["message"])

        post1_chat_collection.insert_one({"message": message, "username": f"{currAuthUser}", "id": id}) #later include what post the chat came from

        response = make_response("", 200)   
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

#method below needs work, not finished
@app.route('/frontpage', methods=['GET']) #gets redirected here after successfully logging in
def displayLoginHomepage():

    username = "changeMe" #determine this based on auth token
    allPostTitles = ["testTitle1", "testTitle2", "testTitle3", "testTitle4", "testTitle5"] #find a way to get a list of every postTitle from the DataBase

    return render_template('loggedin.html', postTitles= allPostTitles, Username = username) #add parameters to replace the html contents

#method below needs work, not finished
@app.route('/frontpage/newPost', methods=['GET','POST']) #gets redirected here after successfully logging in
def addNewPost():
    if request.method == 'GET':
        #just render the template so user can input stuff

        return render_template('newpost.html') #html that will have basic fields of input for user  
    elif request.method == 'POST':
        #maybe new html to add title for post
        #keep track of creation time
        #also keep track of the user of this post
        #initialize likes to 0

        return redirect('/frontpage') #hopefully frontpage will now show the new created post

#method below needs work, not finished
@app.route('/id', methods=['GET']) #gets redirected here to /id after clicking on the first post that is in the loggedin.html
def displaySpecificPost():
    #when js creates GET /id request, itll come from /frontpage after clicking on an existing post, 
    #which should have a unique id to it that every chat message has so we can find only the specific chat messages needed

    return render_template('post.html')


# needs to be 8080
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8080)