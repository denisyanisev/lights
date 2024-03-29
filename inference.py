import cv2
import numpy as np
import os

font = cv2.FONT_HERSHEY_PLAIN
colors = np.random.uniform(0, 255, size=(500, 3))

def load_model():
    net = cv2.dnn.readNet("weights/yolov3_final.weights", "weights/yolov3.cfg")
    classes = []
    with open("weights/yolo.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    return net, output_layers, classes

# Loading camera
def get_result(imagePath, net, output_layers, classes):

    save_path= 'static/uploads/'
    filename= os.path.basename(imagePath).split('.')[0]
    save_filename= os.path.join(save_path, 'pred_'+filename+'.png')

    frame = cv2.imread(imagePath)
    total_lum= 0
    
    height, width, channels = frame.shape

    # Detecting objects
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    # Showing informations on the screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.2:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.25)
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = confidences[i]
            color = colors[class_ids[i]]
            # print(label, confidence)
            if label == 'Street light':
                # luminosity= cal_luminosity(frame[y:y+h, x:x+w])
                total_lum+= 1
                
                # image_save= image[yCoord:endY, xCoord:endX]

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.rectangle(frame, (x, y), (x + w, y + 30), color, -1)
            cv2.putText(frame, label, (x, y + 30), font, 3, (255,255,255), 3)

    cv2.imwrite(save_filename, frame)

    return save_filename, total_lum

# net, output_layers, classes= load_model()
# print(get_result("static/uploads/lamp.jpg", net, output_layers, classes))
