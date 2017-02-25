import os
from squiggly import app
from flask import Flask, request, redirect, render_template, send_from_directory, url_for
from werkzeug.utils import secure_filename
from vision import core as vision
import threading

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('ERR: No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('ERR: No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            fully_qualified_filename = os.path.join(
                app.config['UPLOAD_FOLDER'], filename
            )
            file.save(fully_qualified_filename)
            image_thread = threading.Thread(
                target=process_image,
                args=[fully_qualified_filename]
            )
            image_thread.start()
            return redirect(url_for(
                'uploaded_file', filename=filename
            ))
    return render_template('upload.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'], filename
    )


def process_image(filename):
    return vision.process(filename)
