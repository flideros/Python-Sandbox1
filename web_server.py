import os
from flask import Flask, send_file, send_from_directory

app = Flask(__name__)

@app.route('/<path:filename>')
def serve_mathjax(filename):
    return send_from_directory('mathjax', filename)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jupyter Notebook</title>
    </head>
    <body>
        <h1>Jupyter Notebook</h1>
        <iframe src="http://127.0.0.1:8888/lab" width="100%" height="600px"></iframe>
    </body>
    </html>
    '''
@app.route('/notebooks/<path:filename>')
def serve_notebook(filename):
    return send_file(filename)

if __name__ == '__main__':
    app.run(port=5000, debug=False)