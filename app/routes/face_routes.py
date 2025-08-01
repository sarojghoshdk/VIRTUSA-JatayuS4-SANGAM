from flask import Blueprint, request, session, redirect, jsonify, render_template, url_for
import numpy as np
import cv2
import base64
import os

# Create a Blueprint for face-related routes
face_bp = Blueprint('face', __name__)

# Define the route for the home page
@face_bp.route('/home')
def home():
    # Check if the user is logged in by verifying the session
    if 'username' not in session:
        # Redirect to the login page if not logged in
        return redirect(url_for('auth.login'))
    # Render the home page template if logged in
    return render_template('home.html')

# Define the route for face verification
@face_bp.route('/verify_face', methods=['POST'])
def verify_face():
    # Import necessary libraries for base64 and numpy
    import base64
    import numpy as np

    # Define paths for the model and label files
    model_path = "app/static/face_model.yml"
    label_path = "app/static/label_map.txt"
    
    # Check if the model and label files exist
    if not os.path.exists(model_path) or not os.path.exists(label_path):
        # Return a JSON response indicating the model is not trained
        return jsonify(success=False, message="Model not trained.")

    # Create a face recognizer model using LBPH algorithm
    model = cv2.face.LBPHFaceRecognizer_create()
    # Load the trained model from the specified path
    model.read(model_path)

    # Read the label map from the label file
    with open(label_path, "r") as f:
        # Create a dictionary mapping labels to user names
        label_map = {int(line.split(":")[0]): line.strip().split(":")[1] for line in f}

    # Get the JSON data from the request
    data = request.get_json()
    # Extract the base64 image data from the JSON
    img_data = data['image'].split(',')[1]
    # Decode the base64 image data into a numpy array
    nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
    # Decode the numpy array into an image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # Convert the image to grayscale for face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Load the Haar Cascade classifier for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    # Detect faces in the grayscale image
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Check if any faces were detected
    if len(faces) == 0:
        # Return a JSON response indicating no face was detected
        return jsonify(success=False, message="No face detected.")

    # Extract the coordinates of the first detected face
    (x, y, w, h) = faces[0]
    # Crop the face region from the grayscale image
    face = gray[y:y+h, x:x+w]

    # Predict the label and confidence for the detected face
    label, confidence = model.predict(face)
    # Get the predicted user name from the label map
    predicted_user = label_map.get(label, "unknown")
    # Get the logged-in user's username from the session
    logged_user = session.get("username")

    # Print the predicted user, confidence, and logged-in user for debugging
    print(f"🔍 Predicted: {predicted_user}, Confidence: {confidence}, Logged in: {logged_user}")

    # Only accept if the predicted label matches the logged-in user AND confidence is below threshold
    if predicted_user == logged_user and confidence < 40:
        # Return a JSON response indicating successful verification
        return jsonify(success=True)
    else:
        # Return a JSON response indicating face does not match
        return jsonify(success=False, message="Face not matching")
