"""
Perform detection using models created with the YOLO (You Only Look Once) neural net.
https://pjreddie.com/darknet/yolo/
"""

import cv2
import numpy as np
import os


with open(os.getenv('YOLO_CLASSES_PATH'), 'r') as classes_file:
    classes = dict(enumerate([line.strip() for line in classes_file.readlines()]))
with open(os.getenv('YOLO_CLASSES_OF_INTEREST_PATH'), 'r') as coi_file:
    classes_of_interest = tuple([line.strip() for line in coi_file.readlines()])

def get_bounding_boxes(image):
    # create a YOLO v3 DNN model using pre-trained weights
    net = cv2.dnn.readNet(os.getenv('YOLO_WEIGHTS_PATH'), os.getenv('YOLO_CONFIG_PATH'))
    
    # create image blob
    scale = 0.00392
    image_blob = cv2.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)

    # detect objects
    net.setInput(image_blob)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    outputs = net.forward(output_layers)

    _classes = []
    _confidences = []
    boxes = []
    conf_threshold = float(os.getenv('YOLO_CONFIDENCE_THRESHOLD'))
    nms_threshold = 0.4

    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and classes[class_id] in classes_of_interest:
                width = image.shape[1]
                height = image.shape[0]
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = center_x - w / 2
                y = center_y - h / 2
                _classes.append(classes[class_id])
                _confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    # remove overlapping bounding boxes
    indices = cv2.dnn.NMSBoxes(boxes, _confidences, conf_threshold, nms_threshold)

    _bounding_boxes = []
    for i in indices:
        i = i[0]
        _bounding_boxes.append(boxes[i])

    return _bounding_boxes, _classes, _confidences