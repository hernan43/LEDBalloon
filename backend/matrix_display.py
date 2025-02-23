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

def display_gif(gif_path, forced_loops=1, zero_frame_delay=0.1):
    """Displays a GIF frame by frame on the LED matrix, honoring each frame's delay."""
    global current_gif
    current_gif = os.path.basename(gif_path)

    try:
        with Image.open(gif_path) as gif:
            gif_loop_count = gif.info.get("loop", 1)
            if gif_loop_count == 0:
                gif_loop_count = forced_loops

            if gif.n_frames < 8:
                # Add more loops if it's a short GIF
                gif_loop_count += 1

            for x in range(gif_loop_count):
                if stop_event.is_set():
                    return

                for frame_number, frame in enumerate(ImageSequence.Iterator(gif)):
                    if stop_event.is_set():
                        return
                    
                    # Get the delay for this frame
                    frame_delay = frame.info.get('duration', 0) / 1000.0
                    if frame_delay <= 0:
                        frame_delay = zero_frame_delay

                    # Prepare the frame
                    frame = frame.convert("RGBA").resize((matrix.width, matrix.height))
                    black_bg = Image.new("RGB", frame.size, (0, 0, 0))
                    frame = Image.alpha_composite(black_bg.convert("RGBA"), frame).convert("RGB")
                    
                    # Display the frame
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

    # Load fonts
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    time_font_size = 18
    date_font_size = 10
    time_font = ImageFont.truetype(font_path, time_font_size)
    date_font = ImageFont.truetype(font_path, date_font_size)

    # Get the current time and date
    current_time = time.strftime("%-I:%M %p")
    current_date = time.strftime("%a, %b %d, %Y")

    # Spacing
    time_char_spacing = 0.5
    date_char_spacing = 0.2  # Smaller spacing for date

    # Compute width manually
    time_text_width = sum(time_font.getsize(char)[0] for char in current_time) + (len(current_time) - 1) * time_char_spacing
    date_text_width = sum(date_font.getsize(char)[0] for char in current_date) + (len(current_date) - 1) * date_char_spacing

    # Center both texts horizontally
    start_x_time = (width - time_text_width) // 2
    start_x_date = (width - date_text_width) // 2

    # Calculate vertical positions
    time_y_center = height // 2 - 20
    date_y_offset = 24

    # Draw each character of the time and date with the same sine wave offset
    for i, char in enumerate(current_time):
        offset_y = int(math.sin((frame + i * 2) * 0.2) * 10)
        char_width, char_height = time_font.getsize(char)
        char_x = start_x_time + sum(time_font.getsize(current_time[j])[0] + time_char_spacing for j in range(i))
        draw.text((char_x, time_y_center + offset_y), char, fill="white", font=time_font)

    # Draw the date below the time
    for i, char in enumerate(current_date):
        offset_y = int(math.sin((frame + i * 2) * 0.2) * 10)
        char_width, char_height = date_font.getsize(char)
        char_x = start_x_date + sum(date_font.getsize(current_date[j])[0] + date_char_spacing for j in range(i))
        draw.text((char_x, time_y_center + date_y_offset + offset_y), char, fill="#18453b", font=date_font)

    return image

def display_wavy_clock(interval=10, frame_time=0.01):
    global current_gif
    current_gif = "wavy clock"

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
        clear_matrix(0.1)
        display_wavy_clock()

