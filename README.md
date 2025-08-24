sudo apt update && sudo apt install -y python3-pip python3-venv python3-dev portaudio19-dev libopencv-dev python3-opencv ffmpeg libsm6 libxext6
python3 -m venv aprilenv
source aprilenv/bin/activate
pip install --upgrade pip
pip install flask opencv-python mediapipe SpeechRecognition pyaudio
python app.py
