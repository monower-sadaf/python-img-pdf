from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
from PIL import Image
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Function to check if an extension is valid
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']




@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'files[]' not in request.files:
            return redirect(request.url)
        files = request.files.getlist('files[]')
        
        # List to hold uploaded images
        images = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                images.append(Image.open(filename))
        
        # Convert the list of images to PDF
        if images:
            pdf_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'output.pdf')
            images[0].save(pdf_filename, save_all=True, append_images=images[1:])
            
            # Redirect to the download page
            return redirect(url_for('download_file', filename='output.pdf'))
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)

@app.route('/api/upload', methods=['POST'])
def upload_images():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    files = request.files.getlist('files[]')
    images = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            images.append(Image.open(filename))
    if not images:
        return jsonify({'error': 'No valid images provided'}), 400
    pdf_filename = 'output.pdf'
    images[0].save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename), save_all=True, append_images=images[1:])
    return jsonify({'pdf_url': url_for('download_pdf', filename=pdf_filename, _external=True)})

@app.route('/api/download/<filename>')
def download_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
