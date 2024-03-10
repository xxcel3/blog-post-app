from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/static/<filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5050)