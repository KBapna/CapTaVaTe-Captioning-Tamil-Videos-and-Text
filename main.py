from flask import *
from html.parser import HTMLParser
import subprocess
import sys
import cgi
import os

app = Flask(__name__)

app.config['DOWNLOAD_FOLDER'] = "D:\College\EPICS\captiontesting\captions"

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        file = request.files["file"]
        file.save("D:\\College\\EPICS\\Website\\Uploaded\\"+file.filename) 

        script_path = "D:\\College\\EPICS\Website\\templates\\EPICS.py"
        file_path = "D:\\College\\EPICS\Website\\Uploaded\\"+file.filename
        subprocess.run([sys.executable, script_path, file_path])  
        res = make_response(jsonify({"message" : f"{file.filename} uploaded"}), 200)
        return res


    return render_template('index.html')

@app.route('/about')
def about():

    return render_template('about.html')

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run()




