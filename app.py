# <<<<<<< HEAD
from flask import Flask, render_template, send_from_directory, request, jsonify, make_response, redirect, url_for
from pymongo import MongoClient
import uuid
import json
import html
import bcrypt
import hashlib
import os
from datetime import datetime, timedelta, timezone

# >>>>>>> 21249fd1dcb9d47421bbb0e99b2958b795e1a4db

def remove_slashes(path):
    path_list = path.split("/")
    final_path = ""
    for p in path_list:
        final_path += p
    return final_path
    

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
    filename = remove_slashes(filename)
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
    filename = remove_slashes(filename)
    response = send_from_directory('static/images', filename)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # mime types
    if filename.endswith('.png'):
        response.headers['Content-Type'] = 'image/png'
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        response.headers['Content-Type'] = 'image/jpeg'
    elif filename.endswith('.gif'):
        response.headers['Content-Type'] = 'image/gif'
    elif filename.endswith('.mp4'):
        response.headers['Content-Type'] = 'video/mp4'
    return response

@app.route('/')
def index():
    auth_token = request.cookies.get('auth_token', None)
    # if alr logged in
    if auth_token:
        hashed_auth_token = hashlib.md5(auth_token.encode()).hexdigest()
        user = users_collection.find_one({"auth_token": hashed_auth_token})
        if user:
            if request.method == "GET":
                authToken = request.cookies.get("auth_token")
                hashed_auth_token = hashlib.md5(authToken.encode()).hexdigest()
                userInfo = list(users_collection.find({"auth_token": f"{hashed_auth_token}"}))  
                currAuthUser = userInfo[0]["username"]
                
                query = {
                    "postTitle": {"$exists": True},
                    "username": {"$exists": True},
                    "time": {"$exists": True},
                    "likes": {"$exists": True},
                    "id": {"$exists": True},
                    "image_message": {"$exists": True},
                    "video_message" : {"$exists": True}
                }

                posts_info = list(post_collection.find(query))

                #example below is just hardcoded
                #posts_info = [{"postTitle":"title1", "time":"3-24-2024 12:00:00", "likes": "0"},
                #              {"postTitle":"title2", "time":"3-25-2024 15:05:02", "likes": "10"},
                #              {"postTitle":"title3", "time":"3-20-2024 18:30:45", "likes": "5"}] 

                for post_info in posts_info:
                    post_info['postid'] = str(post_info['id']) 

                response = make_response(render_template('loggedin.html', postsInfo= posts_info, Username = currAuthUser)) #add parameters to replace the html contents
                response.headers['X-Content-Type-Options'] = 'nosniff'

                return response
        else:
            reg_error = request.args.get('reg_error')
            reg_success = request.args.get('reg_success')
            login_error = request.args.get('login_error')
            response = make_response(render_template('index.html', reg_error=reg_error, reg_success=reg_success, login_error=login_error))
            response.headers['X-Content-Type-Options'] = 'nosniff'

            return response
    # otherwise user must login
    else:  
        reg_error = request.args.get('reg_error')
        reg_success = request.args.get('reg_success')
        login_error = request.args.get('login_error')

        response = make_response(render_template('index.html', reg_error=reg_error, reg_success=reg_success, login_error=login_error))
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
        response = make_response(redirect(url_for('index', reg_error="Username is already taken. Please choose a different one.")))
    elif not (username and password and confirm_password):
        response = make_response(redirect(url_for('index', reg_error="Please fill in all necessary fields")))
    elif password != confirm_password:
        response = make_response(redirect(url_for('index', reg_error="Passwords don't match")))
    else:
        # salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt).decode()

        # insert 
        users_collection.insert_one({'username': username, 'password': hashed_password})

        # redirect to homepage 
        response = make_response(redirect(url_for('index', reg_success="Registration successfull")))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username_login')
    password = request.form.get('password_login')

    user = users_collection.find_one({'username': username})
    if not user or not bcrypt.checkpw(password.encode(), user['password'].encode()):
        response = make_response(redirect(url_for('index', login_error="Invalid username or password")))
        response.headers['X-Content-Type-Options'] = 'nosniff'

        return response
    elif not (username and password):
        response = make_response(redirect(url_for('index', login_error="Please fill in all necessary fields")))
        response.headers['X-Content-Type-Options'] = 'nosniff'

        return response
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
    response.set_cookie('auth_token', '', expires=-1)  
    response.headers['X-Content-Type-Options'] = 'nosniff'

    return response

@app.route("/submitNewPost", methods=["POST"])
def add_new_post_after_submit():
    #maybe new html to add title for post
    post_title = html.escape(request.form.get('post-title'))
    post_description = html.escape(request.form.get('post-description'))

    image_message = None
    video_message = None
    # updated here for image
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1] 
        file_path = os.path.join('static/images', filename)
        file.save(file_path)
        if file.mimetype.startswith('image'):
            # Handle image upload
            # image_message = {
            #     "filename": filename,
            #     "filetype": "image"
            # }
            # image_message =  "/" + file_path
            message = f'<img src="static/images/{filename}" alt="Uploaded Image JPEG">'
            content_type = 'image/jpeg'
            
            # image_message = "/" + image_path
        elif file.mimetype.startswith('video'):
            # Handle video upload
            # video_message = "/" + file_path
            message = f'<video width="400" controls autoplay muted><source src="public/images/{filename}" type="video/mp4"></video>'
            content_type = 'video/mp4'


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
    post = {
        "id":id,
        "username": currAuthUser,
        "postTitle": post_title,
        "postDesc": post_description,
        "time":formatted_time, 
        "likes":likes,
        "file_name": filename,
        "message": message
        # "image_message": image_message,
        # "video_message" : video_message  

    }
    post_collection.insert_one(post)

    response = make_response(redirect('/')) #hopefully frontpage will now show the new created post
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.content_type = content_type

    return response

# Where we get messages from DB
@app.route('/id/chat-message', methods=['GET','POST'])
def getMessages():
    if request.method == 'GET':    
        #all the messages from the chat collection of the DB
        #we are going to want to find all chat messages that contains the appropriate postID from the given request and serve those
        allMessages = post1_chat_collection.find({}) 

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

        post1_chat_collection.insert_one({"message": message, "username": f"{currAuthUser}", "id": id}) #later include what post the chat came from with its postID

        response = make_response("", 200)   
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

#can maybe add ajax to listen for new posts to not have to refresh
# @app.route('/frontpage', methods=['GET']) #gets redirected here after successfully logging in
# def displayLoginHomepage():
#     authToken = request.cookies.get("auth_token")
#     hashed_auth_token = hashlib.md5(authToken.encode()).hexdigest()
#     userInfo = list(users_collection.find({"auth_token": f"{hashed_auth_token}"}))  
#     currAuthUser = userInfo[0]["username"]
    
#     query = {
#         "postTitle": {"$exists": True},
#         "username": {"$exists": True},
#         "time": {"$exists": True},
#         "likes": {"$exists": True},
#     }

#     posts_info = list(post_collection.find(query))

#     #example below is just hardcoded
#     #posts_info = [{"postTitle":"title1", "time":"3-24-2024 12:00:00", "likes": "0"},
#     #              {"postTitle":"title2", "time":"3-25-2024 15:05:02", "likes": "10"},
#     #              {"postTitle":"title3", "time":"3-20-2024 18:30:45", "likes": "5"}] 

#     return render_template('loggedin.html', postsInfo= posts_info, Username = currAuthUser) #add parameters to replace the html contents

#maybe error handling when creating a post (ex. can post with empty title/description)
@app.route('/newPost', methods=['GET','POST']) #gets redirected here after successfully logging in
def addNewPost():
    if request.method == 'GET':
        #just render the template so user can input stuff
        authToken = request.cookies.get("auth_token")
        hashed_auth_token = hashlib.md5(authToken.encode()).hexdigest()
        userInfo = list(users_collection.find({"auth_token": f"{hashed_auth_token}"}))
        
        currAuthUser = userInfo[0]["username"]

        response = make_response(render_template('newpost.html', Username=currAuthUser)) #html that will have basic fields of input for user  
        response.headers['X-Content-Type-Options'] = 'nosniff'

        return response

#method below needs work, not finished
#have this request include query string with the postID in which its coming from(might need to create/alter js)
@app.route('/id', methods=['GET']) #gets redirected here to /id after clicking on the first post that is in the loggedin.html
def displaySpecificPost():
    authToken = request.cookies.get("auth_token")
    hashed_auth_token = hashlib.md5(authToken.encode()).hexdigest()
    userInfo = list(users_collection.find({"auth_token": f"{hashed_auth_token}"}))
    currAuthUser = userInfo[0]["username"]

    #based on query string values that has postID, some how let the html update this somehow, 
    #then alter ajax js too notify back end we only want chats tied with that postID

    response = make_response(render_template('post.html', Username=currAuthUser))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    return response

# Add route for recording likes
@app.route('/record-like', methods=['POST'])
def record_like():
    post_id = request.form.get('postid')

    auth_token = request.cookies.get("auth_token")
    hashed_auth_token = hashlib.md5(auth_token.encode()).hexdigest()
    user_info = users_collection.find_one({"auth_token": hashed_auth_token})

    # Get the liked posts from the user
    if user_info:
        liked_posts = user_info.get('liked_posts', [])
        if post_id in liked_posts:
            # redirect the user to another page or display an error message

            response = make_response(redirect("/"))
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            return response

    # update the database to increment the likes for the post with postId
    post = post_collection.find_one({'id': post_id})
    current_likes = int(post.get('likes', 0))
    
    post_collection.update_one({'id': post_id}, {'$set': {'likes': current_likes + 1}})

    # Add the post_id to the liked_posts user's db
    liked_posts.append(post_id)
    users_collection.update_one({"auth_token": hashed_auth_token}, {"$set": {"liked_posts": liked_posts}})

    response = make_response(redirect("/"))
    response.headers['X-Content-Type-Options'] = 'nosniff'

    return response

# add route to unlike
@app.route('/record-unlike', methods=['POST'])
def record_unlike():
    post_id = request.form.get('postid')
    auth_token = request.cookies.get("auth_token")
    hashed_auth_token = hashlib.md5(auth_token.encode()).hexdigest()
    user_info = users_collection.find_one({"auth_token": hashed_auth_token})
    if user_info:
    # get the disliked posts from the user's db
        liked_posts = user_info.get('liked_posts', [])
        if post_id in liked_posts:
            liked_posts.remove(post_id)
            users_collection.update_one({"auth_token": hashed_auth_token}, {"$set": {"liked_posts": liked_posts}})
            post = post_collection.find_one({'id': post_id})
            current_likes = int(post.get('likes', 0))
            post_collection.update_one({'id': post_id}, {'$set': {'likes': current_likes - 1}})
    response = make_response(redirect("/"))
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# needs to be 8080
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8080)