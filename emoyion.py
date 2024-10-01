from flask import Flask, render_template, Response
import cv2
from fer import FER

app = Flask(__name__)

# Initialize the webcam and FER emotion detector
emotion_detector = FER()
cap = cv2.VideoCapture(0)

# Define the emotions that might indicate someone is unwell
unwell_emotions = ['sad', 'fear', 'disgust', 'angry']

# Generator function to stream the video frames with emotion detection
def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Detect emotions in the frame
        emotions = emotion_detector.detect_emotions(frame)

        # Initialize the text to be shown
        text = "Emotion: Unknown"

        if emotions:
            # Get the most likely emotion
            emotion_label = emotions[0]['emotions']
            dominant_emotion = max(emotion_label, key=emotion_label.get)
            
            # Check if the emotion indicates the user might be sick
            if dominant_emotion in unwell_emotions:
                text = f'Looks unwell: {dominant_emotion}'
            else:
                text = f'Emotion: {dominant_emotion}'

            # Display detected emotion on the frame as text
            cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        # Encode the frame as a JPEG image
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield the frame in byte format to be displayed in the HTML
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def emotion_page():
    return render_template('emotion.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
