import os
import threading
import time
from flask import Flask, jsonify, request
from PIL import Image, ImageSequence
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from werkzeug.utils import secure_filename

# Configuration for the LED matrix 
options = RGBMatrixOptions()
options.rows = 64
options.cols = 128
options.chain_length = 1
options.parallel = 1
options.gpio_slowdown = 4  # Adjust if flickering occurs
options.led_rgb_sequence = "BGR"
options.brightness = 60 

# Path to the directory containing GIFs
GIF_DIR = "/opt/gifs"

# Create matrix instance
matrix = RGBMatrix(options=options)

# Flask Web Server Setup
app = Flask(__name__)
current_gif = ""  # Variable to store the currently displayed GIF
app.config['UPLOAD_FOLDER'] = GIF_DIR
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB
ALLOWED_EXTENSIONS = {'gif'}

def allowed_file(filename):
    """Check if the uploaded file has a valid GIF extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_matrix(delay=0.1):
    """Fill the LED matrix with black (turn off all LEDs)."""
    black_image = Image.new("RGB", (matrix.width, matrix.height), (0, 0, 0))
    matrix.SetImage(black_image)
    time.sleep(delay)  # Add delay if you want the black screen to stay for a moment

def display_gif(gif_path):
    """Loads a GIF and displays it frame by frame on the LED matrix."""
    global current_gif
    current_gif = os.path.basename(gif_path)  # Update the currently displayed GIF

    try:
        with Image.open(gif_path) as gif:
            for frame in ImageSequence.Iterator(gif):
                frame = frame.convert("RGBA").resize((matrix.width, matrix.height))  # Resize to fit matrix

                # Fill transparent areas with black
                black_bg = Image.new("RGB", (matrix.width, matrix.height), (0, 0, 0))
                frame = Image.alpha_composite(black_bg.convert("RGBA"), frame).convert("RGB")

                matrix.SetImage(frame)
                time.sleep(0.1)  # Adjust delay between frames
            clear_matrix()
    except Exception as e:
        print(f"Error displaying {gif_path}: {e}")

def gif_display_loop():
    """Loops through all GIFs in the directory and displays them on the matrix."""
    global current_gif
    while True:
        gif_files = [f for f in os.listdir(GIF_DIR) if f.lower().endswith(".gif")]
        for gif in gif_files:
            gif_path = os.path.join(GIF_DIR, gif)
            #print(f"Displaying {gif_path}")
            display_gif(gif_path)

# API Endpoint to get the currently displayed GIF

@app.route('/upload', methods=['POST'])
def upload_gif():
    """Handle GIF upload and save it to the GIF directory."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 200
    
    return jsonify({"error": "Invalid file type, only GIFs are allowed"}), 400

@app.route('/current', methods=['GET'])
def get_current_gif():
    return jsonify({"current_gif": current_gif})

# Start the GIF display loop in a separate thread
def start_display():
    thread = threading.Thread(target=gif_display_loop, daemon=True)
    thread.start()

if __name__ == "__main__":
    start_display()  # Start displaying GIFs
    app.run(host="0.0.0.0", port=5050, load_dotenv=False)  # Start Flask server
    #gif_display_loop()

