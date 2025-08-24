# Update and install system dependencies
sudo apt update && sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    portaudio19-dev \
    libopencv-dev \
    python3-opencv \
    ffmpeg \
    libsm6 \
    libxext6

# Create a virtual environment for April
python3 -m venv aprilenv

# Activate the environment
source aprilenv/bin/activate

# Upgrade pip inside the venv
pip install --upgrade pip

# Install Python dependencies inside venv
pip install flask opencv-python mediapipe SpeechRecognition pyaudio

# Run April (make sure you're in the folder with app.py)
python app.py
