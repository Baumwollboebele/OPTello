import cv2
from tello_controller import Tello



BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                   "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                   "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
                   "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
                ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
                ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
                ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
                ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"] ]

#Path to the Proto and Caffe File
#Proto: Specifies the architecture of the neural network
#Caffe: Stores weights of the trained model
proto_file="/Users/syntax_error/GitHub/op_tello/models/pose/coco/pose_deploy_linevec.prototxt"
weights_file ="/Users/syntax_error/GitHub/op_tello/models/pose/coco/pose_iter_440000.caffemodel"

#Read the neural network into memory
neural_network = cv2.dnn.readNetFromCaffe(proto_file,weights_file)

#tello drone
#cap = cv2.VideoCapture ('udp://@:11111')
#tello = Tello('',8889)

cap = cv2.VideoCapture(0)
"""
The output is a 4D matrix :

The first dimension being the image ID ( in case you pass more than one image to the network ).

The second dimension indicates the index of a keypoint. The model produces Confidence Maps and 
Part Affinity maps which are all concatenated. For COCO model it consists of 57 parts – 18 keypoint 
confidence Maps + 1 background + 19*2 Part Affinity Maps. Similarly, for MPI, it produces 44 points. 
We will be using only the first few points which correspond to Keypoints.

The third dimension is the height of the output map.

The fourth dimension is the width of the output map.
"""

while True:
    
    ret, frame = cap.read()
    frame_width = frame.shape[1]
    frame_height = frame.shape[0]

    inpBlob = cv2.dnn.blobFromImage(frame, 1.0 / 255, (368, 368), (0, 0, 0), swapRB=False, crop=False)

    neural_network.setInput(inpBlob)

    out = neural_network.forward()

    points = []
    for i in range(len(BODY_PARTS)):
        # Slice heatmap of corresponging body's part.
        heatMap = out[0, i, :, :]
    
        # Originally, we try to find all the local maximums. To simplify a sample
        # we just find a global one. However only a single pose at the same time
        # could be detected this way.
        _, conf, _, point = cv2.minMaxLoc(heatMap)
        x = (frame_width * point[0]) / out.shape[3]
        y = (frame_height * point[1]) / out.shape[2]
    
        # Add a point if it's confidence is higher than threshold.
        points.append((int(x), int(y)) if conf > 0.1 else None)
        

    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        assert(partFrom in BODY_PARTS)
        assert(partTo in BODY_PARTS)

        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]
        if points[idFrom] and points[idTo]:
            cv2.line(frame, points[idFrom], points[idTo], (255, 74, 0), 3)
            cv2.ellipse(frame, points[idFrom], (4, 4), 0, 0, 360, (255, 255, 255), cv2.FILLED)
            cv2.ellipse(frame, points[idTo], (4, 4), 0, 0, 360, (255, 255, 255), cv2.FILLED)
            cv2.putText(frame, str(idFrom), points[idFrom], cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255),2,cv2.LINE_AA)
            cv2.putText(frame, str(idTo), points[idTo], cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255),2,cv2.LINE_AA)


    cv2.imshow(f"Output-Keypoints",frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        out = cv2.imwrite('capture.jpg', frame)
        break

cap.release()
cv2.destroyAllWindows()