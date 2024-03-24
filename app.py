# <<<<<<< HEAD
from flask import Flask, render_template, send_from_directory, request, jsonify, make_response, redirect, url_for
from pymongo import MongoClient
import uuid
import json
import html
import bcrypt
import hashlib
from datetime import datetime, timedelta, timezone

# >>>>>>> 21249fd1dcb9d47421bbb0e99b2958b795e1a4db

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'
# app.config['MONGO_URI'] = 'mongodb://localhost:27017/users'
mongo_client = MongoClient("mongo", 27017)
db = mongo_client["cse312_Group_Project"]
users_collection = db['users']

post1_chat_collection = db["post1_chat"] # we need to find a way to create unique chat collections per unique posts
post_collection = db["posts"] # every post should keep track of user who posted and time of post creation, maybe number of current likes(might have to use ajax to update this)

@app.route('/static/<filename>')
def serve_static(filename):
    response = send_from_directory('static', filename)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # mime types
    if filename.endswith('.css'):
        response.headers['Content-Type'] = 'text/css'
    elif filename.endswith('.js'):
        response.headers['Content-Type'] = 'application/javascript'
    return response

@app.route('/static/images/<filename>')
def serve_images(filename):
    response = send_from_directory('static/images', filename)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # mime types
    if filename.endswith('.png'):
        response.headers['Content-Type'] = 'image/png'
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        response.headers['Content-Type'] = 'image/jpeg'
    return response

@app.route('/')
def index():
    auth_token = request.cookies.get('auth_token', None)
    # if alr logged in
    if auth_token:
        hashed_auth_token = hashlib.md5(auth_token.encode()).hexdigest()
        user = users_collection.find_one({"auth_token": hashed_auth_token})
        if user:
            return render_template("loggedin.html")
            # response = make_response(redirect("/"))
    # otherwise user must login
    else:  
        error = request.args.get('error')
        login_error = request.args.get('login_error')
        response = make_response(render_template('index.html', error=error, login_error=login_error))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username_reg')
    password = request.form.get('password_reg')
    confirm_password = request.form.get('password_reg_confirm')

    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        # redirect to homepage with an error message
        response = make_response(redirect(url_for('index', error="Username is already taken. Please choose a different one.")))
    elif not (username and password and confirm_password):
        response = make_response(redirect(url_for('index', error="Please fill in all necessary fields")))
    elif password != confirm_password:
        response = make_response(redirect(url_for('index', error="Passwords don't match")))
    else:
        # salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt).decode()

        # insert 
        users_collection.insert_one({'username': username, 'password': hashed_password})

        # redirect to homepage 
               
        response = make_response(redirect(url_for('index', success="Registration successfull")))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username_login')
    password = request.form.get('password_login')

    user = users_collection.find_one({'username': username})
    if not user or not bcrypt.checkpw(password.encode(), user['password'].encode()):
        return redirect(url_for('index', login_error="Invalid username or password"))
    elif not (username and password):
        return redirect(url_for('index', login_error="Please fill in all necessary fields"))
    else:
        # generate authentication token
        token = str(uuid.uuid4())
        # hashed token in database
        hashed_auth_token = hashlib.md5(token.encode()).hexdigest()
        users_collection.update_one({'username': username}, {'$set': {'auth_token': hashed_auth_token}})

        # set authentication token as HttpOnly cookie
        response = make_response(redirect("/"))
        response.set_cookie('auth_token', token, httponly=True, expires=datetime.now() + timedelta(hours=1))
        response.headers['X-Content-Type-Options'] = 'nosniff'

        return response
    
@app.route('/logout', methods=['POST'])
def logout():
    auth_token = request.cookies.get('auth_token')  
    hashed_auth_token = hashlib.md5(auth_token.encode()).hexdigest()

    # remove auth token 
    users_collection.update_one({'auth_token': hashed_auth_token}, {'$unset': {'auth_token': ""}})

    # clear the auth token cookie 
    response = make_response(redirect(url_for('index')))
    response.set_cookie('auth_token', '', expires=0)  
    response.headers['X-Content-Type-Options'] = 'nosniff'

    return response

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
        hashed_auth_token = hashlib.md5(authToken.encode()).hexdigest()
        userInfo = list(users_collection.find({"auth_token": f"{hashed_auth_token}"}))
        
        currAuthUser = userInfo[0]["username"]

        data = request.json
        message = html.escape(data["message"])

        post1_chat_collection.insert_one({"message": message, "username": f"{currAuthUser}", "id": id}) #later include what post the chat came from

        response = make_response("", 200)   
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

#can maybe add ajax to listen for new posts to not have to refresh
@app.route('/frontpage', methods=['GET']) #gets redirected here after successfully logging in
def displayLoginHomepage():
    authToken = request.cookies.get("auth_token")
    hashed_auth_token = hashlib.md5(authToken.encode()).hexdigest()
    userInfo = list(users_collection.find({"auth_token": f"{hashed_auth_token}"}))  
    currAuthUser = userInfo[0]["username"]
    
    query = {
        "postTitle": {"$exists": True},
        "username": {"$exists": True},
        "time": {"$exists": True},
        "likes": {"$exists": True},
    }

    posts_info = list(post_collection.find(query))

    #example below is just hardcoded
    #posts_info = [{"postTitle":"title1", "time":"3-24-2024 12:00:00", "likes": "0"},
    #              {"postTitle":"title2", "time":"3-25-2024 15:05:02", "likes": "10"},
    #              {"postTitle":"title3", "time":"3-20-2024 18:30:45", "likes": "5"}] 

    return render_template('loggedin.html', postsInfo= posts_info, Username = currAuthUser) #add parameters to replace the html contents

#maybe error handling when creating a post (ex. can post with empty title/description)
@app.route('/frontpage/newPost', methods=['GET','POST']) #gets redirected here after successfully logging in
def addNewPost():
    if request.method == 'GET':
        #just render the template so user can input stuff
        authToken = request.cookies.get("auth_token")
        hashed_auth_token = hashlib.md5(authToken.encode()).hexdigest()
        userInfo = list(users_collection.find({"auth_token": f"{hashed_auth_token}"}))
        
        currAuthUser = userInfo[0]["username"]
        return render_template('newpost.html', Username=currAuthUser) #html that will have basic fields of input for user  
    
    elif request.method == 'POST':
        #maybe new html to add title for post
        post_title = html.escape(request.form.get('post-title'))
        post_description = html.escape(request.form.get('post-description'))

        #keep track of creation time
        current_time = datetime.now()
        offset = timedelta(hours=-4)
        current_time = current_time.replace(tzinfo=timezone.utc) + offset   #adding offset to get eastern time
        formatted_time = current_time.strftime("%m-%d-%Y %H:%M:%S")

        #also keep track of the user of this post
        authToken = request.cookies.get("auth_token")
        hashed_auth_token = hashlib.md5(authToken.encode()).hexdigest()
        userInfo = list(users_collection.find({"auth_token": f"{hashed_auth_token}"}))
        
        currAuthUser = userInfo[0]["username"]

        #initialize likes to 0 and create id
        id = str(uuid.uuid4())
        likes = "0"
        
        #inserting newly created post to db
        post_collection.insert_one({"id":id, "username": currAuthUser, "postTitle": post_title, "postDesc":post_description, "time":formatted_time, "likes":likes})

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