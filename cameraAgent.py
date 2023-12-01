#use python version 3.11.x
#pip install roboflow supervision
#pip install numpy
import numpy as np
import supervision as sv
from roboflow import Roboflow
from dotenv import load_dotenv
import os
import tempfile
load_dotenv()

#SOURCE_VIDEO_PATH = "videoTest.mp4"
SOURCE_VIDEO_PATH = "seq1.mp4"
TARGET_VIDEO_PATH = "seq1_output.mp4"

# use https://roboflow.github.io/polygonzone/ to get the points for your line
polygon = np.array([
    # draw 50x50 box in top left corner
    [0, 0],
    [50, 0],
    [50, 50],
    [0, 50]
])

rf = Roboflow(api_key = os.getenv('ROBOFLOW_API_KEY'))
project = rf.workspace().project("tc2008")
model = project.version(1).model

# create BYTETracker instance
byte_tracker = sv.ByteTrack(track_thresh=0.80, track_buffer=30, match_thresh=0.8, frame_rate=30)

# create VideoInfo instance
video_info = sv.VideoInfo.from_video_path(SOURCE_VIDEO_PATH)

# create frame generator
generator = sv.get_video_frames_generator(SOURCE_VIDEO_PATH)

# create PolygonZone instance
zone = sv.PolygonZone(polygon=polygon, frame_resolution_wh=(video_info.width, video_info.height))

# create box annotator
box_annotator = sv.BoxAnnotator(thickness=4, text_thickness=4, text_scale=1)

colors = sv.ColorPalette.default()

# create instance of BoxAnnotator
zone_annotator = sv.PolygonZoneAnnotator(thickness=4, text_thickness=4, text_scale=2, zone=zone, color=colors.colors[0])

# define call back function to be used in video processing
def callback(frame: np.ndarray, index:int) -> np.ndarray:
    # model prediction on single frame
    results = model.predict(frame).json()

    # Filter out detections with confidence lower than 0.80
    results['predictions'] = [d for d in results['predictions'] if d['confidence'] >= 0.80]

    # Convert to supervision Detections
    detections = sv.Detections.from_roboflow(results)

    # show detections in real time
    print(detections)

    # tracking detections
    tracked_detections = byte_tracker.update_with_detections(detections)

    # Extract class names and other details from detections
    labels = [
        f"#{tracker_id} {detection['class']} {confidence:0.8f}"
        for detection, (_, _, confidence, _, tracker_id) in zip(results['predictions'], tracked_detections)
    ]

    annotated_frame = box_annotator.annotate(scene=frame, detections=tracked_detections, labels=labels)

    annotated_frame = zone_annotator.annotate(scene=annotated_frame)
    return annotated_frame

# process the whole video
sv.process_video(
    source_path = SOURCE_VIDEO_PATH,
    target_path = TARGET_VIDEO_PATH,
    callback=callback
)