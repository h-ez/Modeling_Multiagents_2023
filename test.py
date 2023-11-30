import os
from roboflow import Roboflow
from dotenv import load_dotenv 

load_dotenv()

# Initialize Roboflow model
rf = Roboflow(api_key=os.getenv('ROBOFLOW_API_KEY'))
project = rf.workspace().project("tc2008")
model = project.version(1).model

# Directory containing images
image_dir = "camera1Images"

# Iterate through each file in the directory
for file in os.listdir(image_dir):
    # Check if the file is a PNG image
    if file.endswith(".png"):
        # Construct the full path to the image
        image_path = os.path.join(image_dir, file)

        # Perform prediction and get JSON result
        json_output = model.predict(image_path, confidence=70, overlap=30).json()

        # Check if there is a 'full_truck' class in predictions
        for prediction in json_output['predictions']:
            if prediction['class'] == 'full_truck':
                print(f"Full truck found in {file}: {prediction}")
                break  # Exit the loop after finding 'full_truck'

        # If a 'full_truck' class was found, exit the outer loop
        if any(prediction['class'] == 'full_truck' for prediction in json_output['predictions']):
            break
