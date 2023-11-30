import os
from roboflow import Roboflow
from dotenv import load_dotenv 

load_dotenv()

# Initialize Roboflow model
rf = Roboflow(api_key=os.getenv('ROBOFLOW_API_KEY'))
project = rf.workspace().project("tc2008")
model = project.version(1).model

# Directories containing images
camera_dirs = ["camera1Images", "camera2Images", "camera3Images"]

# Iterate through each camera directory
for camera_dir in camera_dirs:
    print(f"Processing images from: {camera_dir}")

    # Iterate through each file in the current directory
    for file in os.listdir(camera_dir):
        # Check if the file is a PNG image
        if file.endswith(".png"):
            # Construct the full path to the image
            image_path = os.path.join(camera_dir, file)

            # Perform prediction and get JSON result
            json_output = model.predict(image_path, confidence=70, overlap=30).json()

            # Check if there is a 'full_truck' class in predictions
            for prediction in json_output['predictions']:
                if prediction['class'] == 'full_truck':
                    print(f"Full truck found in {file} in directory {camera_dir}: {prediction}")
                    break  # Exit the loop after finding 'full_truck'

            # If a 'full_truck' class was found, exit the outer loop
            if any(prediction['class'] == 'full_truck' for prediction in json_output['predictions']):
                break

    print(f"Finished processing images from: {camera_dir}")
