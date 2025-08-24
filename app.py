# app.py - Python Backend for the Raspberry Pi Voice Assistant

from flask import Flask, render_template, request, Response, jsonify
from gtts import gTTS
import os
import io
import cv2
import threading
import time

# Initialize Flask application
app = Flask(__name__)

# --- Video Stream Logic ---
video_stream = None
video_thread = None
frame_lock = threading.Lock()
is_camera_running = False

def generate_frames():
    """Generates frames from the webcam for the video stream."""
    global video_stream, is_camera_running

    if not is_camera_running:
        video_stream = cv2.VideoCapture(0)  # This should automatically find your Logitech webcam
        if not video_stream.isOpened():
            print("Error: Could not open video stream.")
            return

    is_camera_running = True
    while is_camera_running:
        success, frame = video_stream.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
        time.sleep(0.033)  # Roughly 30 FPS

@app.route('/video_feed')
def video_feed():
    """Serves the live video stream."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera', methods=['POST'])
def start_camera():
    """Starts the webcam video stream."""
    global video_thread
    if video_thread is None or not video_thread.is_alive():
        video_thread = threading.Thread(target=lambda: Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame'))
        video_thread.daemon = True
        video_thread.start()
    return jsonify(success=True)

# --- Voice Assistant Logic ---
@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/voice_command', methods=['POST'])
def voice_command():
    """Receives voice command, processes it, and returns an audio response."""
    try:
        data = request.json
        command_text = data.get('command', '').lower()
        print(f"Received command: '{command_text}'")

        response_text = "I'm sorry, I didn't get that. Could you please repeat?"

        # A simplified LLM call to process the command.
        # This is a placeholder for your own logic or a real API call.
        if "hello xeno" in command_text:
            response_text = "Hello there. How can I assist you today?"
        elif "what is the time" in command_text:
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            response_text = f"The current time is {current_time}."
        elif "take a picture" in command_text:
            response_text = "I am ready to take a picture. Say 'cheese' to capture the moment."
        elif "goodbye" in command_text:
            response_text = "Goodbye! I'm here if you need me again."
        
        # Additional logic for specific commands, like image capture
        if "cheese" in command_text and "take a picture" in command_text:
            ret, frame = video_stream.read()
            if ret:
                image_name = f'capture_{int(time.time())}.jpg'
                cv2.imwrite(image_name, frame)
                response_text = f"I captured the image and saved it as {image_name}."
            else:
                response_text = "I couldn't capture the image."
            
        # Generate speech from the response text using gTTS
        tts = gTTS(text=response_text, lang='en')
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)
        
        return Response(audio_stream.read(), mimetype="audio/mp3")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        error_message = f"An error occurred: {e}"
        tts = gTTS(text=error_message, lang='en')
        audio_stream = io.BytesIO()
        tts.write_to_fp(audio_stream)
        audio_stream.seek(0)
        return Response(audio_stream.read(), mimetype="audio/mp3")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
