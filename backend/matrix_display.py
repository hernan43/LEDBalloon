import math
import os
import threading
import time
from PIL import Image, ImageSequence, ImageDraw, ImageFont
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from datetime import datetime

# Matrix configuration
options = RGBMatrixOptions()
options.rows = 64
options.cols = 128 
options.chain_length = 1
options.parallel = 1
options.gpio_slowdown = 4
options.led_rgb_sequence = "BGR"
options.brightness = 50

matrix = RGBMatrix(options=options)

# Path to the GIF directory
GIF_DIR = "/opt/gifs"
current_gif = None
stop_event = threading.Event()

def display_gif(gif_path, frame_delay=0.10, forced_loops=2):
    """Displays a GIF frame by frame on the LED matrix."""
    global current_gif
    current_gif = os.path.basename(gif_path)

    try:
        with Image.open(gif_path) as gif:

            gif_loop_count = gif.info.get("loop", 1)
            if gif_loop_count == 0:
                gif_loop_count = forced_loops

            if gif.n_frames < 8:
                # add more if it is a short one
                gif_loop_count += forced_loops

            for x in range(gif_loop_count):
                #print(f"Playing {gif_path}({gif.n_frames}) count {x+1}")

                if stop_event.is_set():
                    return

                for frame in ImageSequence.Iterator(gif):
                    if stop_event.is_set():
                        return
                    frame = frame.convert("RGBA").resize((matrix.width, matrix.height))
                    black_bg = Image.new("RGB", frame.size, (0, 0, 0))
                    frame = Image.alpha_composite(black_bg.convert("RGBA"), frame).convert("RGB")
                    matrix.SetImage(frame)
                    time.sleep(frame_delay)

                    if stop_event.is_set():
                        return


    except Exception as e:
        print(f"Error displaying {gif_path}: {e}")

def clear_matrix(delay=0.5):
    """Clears the matrix by showing a black screen."""
    black_image = Image.new("RGB", (matrix.width, matrix.height), (0, 0, 0))
    matrix.SetImage(black_image)
    time.sleep(delay)

def display_time(interval=10):
    """Displays the current time on the matrix."""
    global current_gif
    current_gif = "clock"

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font = ImageFont.truetype(font_path, 24)

    for _ in range(interval):  # Show time for interval
        if stop_event.is_set():
            return

        now = datetime.now().strftime("%H:%M:%S")
        image = Image.new("RGB", (matrix.width, matrix.height), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        text_width, text_height = draw.textsize(now, font=font)
        x = (matrix.width - text_width) // 2
        y = (matrix.height - text_height) // 2

        draw.text((x, y), now, font=font, fill=(255, 255, 255))
        matrix.SetImage(image)

        time.sleep(1)

def create_wavy_clock_frame(width, height, frame):
    image = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(image)

    # Load a font
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size = 24  # Adjust font size for better fit
    font = ImageFont.truetype(font_path, font_size)

    # Get the current time
    current_time = time.strftime("%H:%M:%S")

    # Fixed spacing between characters
    char_spacing = 1  # Adjust spacing as needed

    # Compute width manually (fixes missing characters issue)
    text_width = sum(font.getsize(char)[0] for char in current_time) + (len(current_time) - 1) * char_spacing

    # Center the text horizontally
    start_x = (width - text_width) // 2

    # Draw each character with a vertical sine wave effect
    x = start_x
    for i, char in enumerate(current_time):
        offset_y = int(math.sin((frame + i * 2) * 0.2) * 10)  # Wavy motion
        char_width, char_height = font.getsize(char)
        char_y = (height // 2) - (char_height // 2) + offset_y

        draw.text((x, char_y), char, fill="white", font=font)

        # Move x forward by character width + spacing
        x += char_width + char_spacing

    return image

def display_wavy_clock(interval=10, frame_time=0.03):
    frame = 0
    start_time = time.time()

    while time.time() - start_time < interval:  # Show time for interval
        if stop_event.is_set():
            return

        image = create_wavy_clock_frame(matrix.width, matrix.height, frame)
        matrix.SetImage(image.convert("RGB"))
        frame += 1
        time.sleep(frame_time)

def get_current_gif():
    """Returns the currently displayed GIF."""
    return current_gif

def iterate_gifs():
    """Continuously iterates through GIFs in the directory."""
    while True:
        gif_files = [f for f in os.listdir(GIF_DIR) if f.lower().endswith('.gif')]
        if not gif_files:
            clear_matrix()
            time.sleep(5)
            continue

        for gif in gif_files:
            if stop_event.is_set():
                stop_event.clear()  # Reset the event for normal iteration
            display_gif(os.path.join(GIF_DIR, gif))

        # Show time after completing a full GIF loop
        #display_time()
        display_wavy_clock()

