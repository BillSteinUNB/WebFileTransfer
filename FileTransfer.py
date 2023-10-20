import os
from flask import Flask, render_template, send_from_directory, request, redirect, url_for
import pyqrcode
import socket
import webbrowser
from flask_uploads import UploadSet, configure_uploads, IMAGES, DOCUMENTS
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__, static_folder='nonexistent_folder')
app.config['SECRET_KEY'] = 'yoursecretkey'

csrf = CSRFProtect(app)
# The directory you want to share
SHARED_FOLDER = os.path.join(os.path.join(os.environ['USERPROFILE']), 'FileShareNetworkFolder')
PORT = 8010

# Configure file uploads
files = UploadSet('files', IMAGES + DOCUMENTS)
app.config['UPLOADED_FILES_DEST'] = SHARED_FOLDER
configure_uploads(app, files)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = UploadForm()
    files_list = os.listdir(SHARED_FOLDER)

    if form.validate_on_submit():
        filename = files.save(form.photo.data)
        return redirect(url_for('index'))

    return render_template('index.html', files=files_list, form=form)


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(SHARED_FOLDER, filename, as_attachment=True)

class UploadForm(FlaskForm):
    photo = FileField(validators=[FileRequired()]) 

def generate_qr(link):
    url = pyqrcode.create(link)
    qr_path = os.path.join(SHARED_FOLDER, "myqr.svg")
    url.svg(qr_path, scale=8)
    webbrowser.open(qr_path)

if __name__ == '__main__':
    # Determine the IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = "http://" + s.getsockname()[0] + ":" + str(PORT)
    
    # Generate QR code for the IP address
    generate_qr(IP)
    
    print("Serving at port", PORT)
    print("Type this in your Browser:", IP)
    print("Or use the QRCode")
    
    app.run(host='0.0.0.0', port=PORT, debug=True)
