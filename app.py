from flask import Flask, render_template
from pymongo import MongoClient

mongo_client = MongoClient("mongo", 27018)
db = mongo_client["cse312_Group_Project"]
#chat_collection = db["chat"] can fill DB with collections as we need them

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host= "0.0.0.0" ,debug=True, port=5050)