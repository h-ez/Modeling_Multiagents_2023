#pip install roboflow
from dotenv import load_dotenv
import os
from roboflow import Roboflow

load_dotenv()
#rf = Roboflow(api_key="P9KUrFkOZXUp594HiMdX")
rf = Roboflow(api_key = os.getenv('ROBOFLOW_API_KEY'))
project = rf.workspace().project("tc2008")
model = project.version(1).model

# infer on a local image
#print(model.predict("your_image.jpg", confidence=40, overlap=30).json())

# visualize your prediction
# model.predict("your_image.jpg", confidence=40, overlap=30).save("prediction.jpg")

# infer on an image hosted elsewhere
print(model.predict("https://github.com/h-ez/Modeling_Multiagents_2023/blob/main/Pictures/DumpTruckData/FirstBatch/EmptyDumpTruck/Screenshot%202023-11-26%20133554.png?raw=true", hosted=True, confidence=40, overlap=30).json())