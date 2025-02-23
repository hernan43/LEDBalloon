from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging
import os
import matrix_display
import threading

app = Flask(__name__)
CORS(app)

# Server configuration
GIF_DIR = "/opt/gifs"
app.config['UPLOAD_FOLDER'] = GIF_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit
logging.getLogger('flask_cors').level = logging.DEBUG

ALLOWED_EXTENSIONS = {'gif'}

def allowed_file(filename):
    """Check if the uploaded file is a GIF."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.after_request
def apply_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'  # Allows all origins
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'  # Allows these methods
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'  # Allow these headers
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    return response

@app.route('/upload', methods=['POST'])
def upload_gif():
    """Upload a new GIF to the server and immediately play it."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Interrupt and play the new GIF
        matrix_display.stop_event.set()
        threading.Thread(target=matrix_display.display_gif, args=(file_path,)).start()

        return jsonify({"message": "File uploaded and playing", "filename": filename}), 200
    
    return jsonify({"error": "Invalid file type, only GIFs are allowed"}), 400

@app.route('/current', methods=['GET'])
def current_gif():
    """Get the currently displayed GIF."""
    gif_name = matrix_display.get_current_gif()
    if gif_name:
        return jsonify({"current_gif": gif_name}), 200
    return jsonify({"message": "No GIF is currently playing"}), 404

if __name__ == "__main__":
    # Start automatic GIF iteration in a separate thread
    threading.Thread(target=matrix_display.iterate_gifs, daemon=True).start()
    app.run(host="0.0.0.0", port=5050, load_dotenv=False)

