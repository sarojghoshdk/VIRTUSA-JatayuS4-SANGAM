import cv2  # Importing OpenCV library for image processing
import numpy as np  # Importing NumPy for numerical operations
import os  # Importing os module for file and directory operations

def extract_base_username(filename):
    """
    Extracts username from filename:
    - admin_master_1.jpg → admin_master
    - emp_kolkata_01_3.jpg → emp_kolkata_01
    """
    name = os.path.splitext(filename)[0]  # Remove file extension from filename
    parts = name.split('_')  # Split the filename into parts using underscore as delimiter
    if parts[-1].isdigit():  # Check if the last part is a digit
        return '_'.join(parts[:-1])  # drop the trailing index and return the base username
    return name  # Return the original name if no trailing index is found

def train_all_faces(folder_path='app/static/user_faces'):
    print("Starting face training...")  # Indicate the start of the training process

    if not os.path.exists(folder_path):  # Check if the specified folder exists
        print(f"Folder '{folder_path}' does not exist.")  # Notify if the folder is missing
        return  # Exit the function if the folder does not exist

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")  # Load the face detection model
    model = cv2.face.LBPHFaceRecognizer_create()  # Create a Local Binary Patterns Histograms face recognizer

    faces = []  # Initialize a list to hold detected face images
    labels = []  # Initialize a list to hold corresponding labels for the faces
    label_map = {}  # Dictionary to map label IDs to usernames
    label_ids = {}  # Dictionary to store unique IDs for each username
    current_id = 0  # Initialize a counter for unique label IDs

    files = os.listdir(folder_path)  # List all files in the specified folder
    print(f"Found {len(files)} files in {folder_path}")  # Notify how many files were found

    for filename in files:  # Iterate through each file in the folder
        if filename.lower().endswith(('.jpg', '.png', '.jpeg')):  # Check if the file is an image
            path = os.path.join(folder_path, filename)  # Create the full path to the image file
            username = extract_base_username(filename)  # Extract the base username from the filename
            print(f"Processing image: {filename} → user: '{username}'")  # Notify which image is being processed

            if username not in label_ids:  # Check if the username is already assigned a label ID
                label_ids[username] = current_id  # Assign a new ID to the username
                label_map[current_id] = username  # Map the ID to the username
                current_id += 1  # Increment the ID counter

            label = label_ids[username]  # Retrieve the label ID for the current username

            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)  # Read the image in grayscale
            if img is None:  # Check if the image was read successfully
                print(f"Could not read image: {filename}")  # Notify if the image could not be read
                continue  # Skip to the next file

            detected = face_cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=5)  # Detect faces in the image
            if len(detected) == 0:  # Check if any faces were detected
                print(f"No face found in {filename}. Skipping.")  # Notify if no face was found
                continue  # Skip to the next file

            (x, y, w, h) = detected[0]  # Get the coordinates and dimensions of the first detected face
            face = img[y:y+h, x:x+w]  # Extract the face from the image using the coordinates
            faces.append(face)  # Add the extracted face to the faces list
            labels.append(label)  # Add the corresponding label to the labels list
            print(f"Face added for '{username}' (label {label})")  # Confirm that the face was added

    if not faces:  # Check if no valid faces were found
        print("No valid faces found. Training aborted.")  # Notify that training cannot proceed
        return  # Exit the function

    print(f"Training model with {len(faces)} faces...")  # Indicate the number of faces being used for training
    model.train(faces, np.array(labels))  # Train the model using the collected faces and labels

    os.makedirs("app/static", exist_ok=True)  # Create the directory for saving the model if it doesn't exist
    model.save("app/static/face_model.yml")  # Save the trained model to a file
    print("Model saved at app/static/face_model.yml")  # Confirm that the model was saved

    with open("app/static/label_map.txt", "w") as f:  # Open a file to save the label map
        for id_, name in label_map.items():  # Iterate through the label map
            f.write(f"{id_}:{name}\n")  # Write each ID and username to the file

    print("Label map saved at app/static/label_map.txt")  # Confirm that the label map was saved
    print("Training complete!")  # Indicate that the training process is finished

if __name__ == "__main__":  # Check if the script is being run directly
    train_all_faces()  # Call the function to start training faces

