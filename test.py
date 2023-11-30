import os
from roboflow import Roboflow

# Initialize Roboflow model
rf = Roboflow(api_key = os.getenv('ROBOFLOW_API_KEY'))
project = rf.workspace().project("tc2008")
model = project.version(1).model

# Directory containing images
image_dir = "camera1Images"

# Array to store JSON results
predictions_camera_one = []

# Iterate through each file in the directory
for file in os.listdir(image_dir):
    # Check if the file is a PNG image
    if file.endswith(".png"):
        # Construct the full path to the image
        image_path = os.path.join(image_dir, file)

        # Perform prediction and get JSON result
        json_output = model.predict(image_path, confidence=70, overlap=30).json()

        # Append the result to the array
        predictions_camera_one.append(json_output)

# Print or process the array of JSON results as needed
print(predictions_camera_one)
