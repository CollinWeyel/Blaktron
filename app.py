from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from threading import Thread

import os
import hashlib
import serial
import mido

#Change working directory to current directory
os.chdir(os.path.dirname(__file__))

#Config data
UPLOAD_FOLDER = os.getcwd() + '/uploads'
TEMP_FOLDER = os.getcwd() + '/temp'
ALLOWED_EXTENSIONS = set(['midi', 'mid'])

SEPERATOR='_:#:_'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

#Create application
app = Flask(__name__)

#Configure application
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER

#Music variables
thread = ""
stop = False
plaing = False

#Debug variables
not_existent = True

#Help functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def prevent_file_override_name(file):
    filename = file.filename
    file.save(os.path.join(app.config['TEMP_FOLDER'], filename))
    md5 = hashlib.md5()

    with open(os.path.join(app.config['TEMP_FOLDER'], filename), 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    os.remove(os.path.join(app.config['TEMP_FOLDER'], filename))
    return md5.hexdigest() + SEPERATOR + secure_filename(file.filename)

def get_uploaded_files():
    path = app.config['UPLOAD_FOLDER']
    files = []
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            files.append({'filename':file, 'name':file.split(SEPERATOR, 1)[1] \
                            .rsplit('.', 1)[0].replace('_', ' ')})
    return files

def play(midi):
    global plaing
    global stop

    plaing = True
    mido.set_backend('serial_output')

    print("Started playing: ", midi)

    with mido.open_output() as port:
        print('Using {}.'.format(port))

        for msg in mido.MidiFile(os.path.join(UPLOAD_FOLDER, midi)).play():
            if stop:
                break
            port.send(msg)


#Server routes
@app.route("/")
def index():
    return redirect(url_for('cp_0'))

@app.route("/cp")
def cp_0():
    return render_template("index.html", files=get_uploaded_files())

@app.route("/cp/<upload>")
def cp_1(upload):
    files = get_uploaded_files()
    return render_template("index.html", upload=upload, files=files)

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        #Isn't a file part in the post request?
        if 'file' not in request.files:
            flash('No file part!')
            return redirect(url_for('cp_1', upload='error'))
        file = request.files['file']

        #Is a file selected?
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('cp_1', upload='error'))

        #Is file allowed to be uploaded
        #Then save
        if file and allowed_file(file.filename):
            filename = prevent_file_override_name(file)
            file.stream.seek(0)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('cp_1', upload='succsess'))

@app.route("/write", methods=['POST'])
def write():
    global thread
    global plaing
    global stop
    if plaing:
        stop = True
        thread.join()
        stop = False
    thread = Thread(target=play, args=(request.form['midi'],))
    thread.start()
    return redirect(url_for('cp_1', upload='playing'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
