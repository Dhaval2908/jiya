import os
import subprocess
from pathlib import Path
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename


# Initialize the Flask application
app = Flask(__name__)

# Set up app configurations
app.config['SECRET_KEY'] = os.urandom(16)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'cc'}


####################
# Helper functions #
####################

def allowed_file(filename):
    """Check if the file type is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_uploaded_file():
    """Get the path of the uploaded file."""
    file_path = os.path.join(os.getcwd(), 'compile.py')
    return file_path



def compile_file(file_path):
    """Compile the uploaded file."""
    try:
        output = subprocess.check_output(['python', 'compile.py', str(file_path)])

    except subprocess.TimeoutExpired:
        return None
    output = output.decode('utf-8')
    return output


########################
# Route and view logic #
########################

@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Handle file uploading."""
    if request.method == 'POST':
        # Check if the request contains a file
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        # Get the uploaded file
        file = request.files['file']

        # Check if the file was selected
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Check if the file type is allowed
        if not allowed_file(file.filename):
            flash('Invalid file type')
            return redirect(request.url)

        # Save the uploaded file
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Redirect to the compile route
        return redirect(url_for('compile'))

    # Render the upload page for a GET request
    return render_template('upload.html')


@app.route('/compile')
def compile():
    """Compile the uploaded file and render the result page."""
    file_path = get_uploaded_file()
    output = compile_file(file_path)
    output= f'<pre>{output}</pre>'
    return render_template('result.html', output=output)


if __name__ == '__main__':
    # Start the app
    app.run(host='0.0.0.0', debug=True)