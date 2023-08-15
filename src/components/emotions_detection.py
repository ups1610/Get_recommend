import os 
import sys
from src.logger import logging
from src.exception import CustomException
from dataclasses import dataclass
from src.components.model_training import BuildModel
import cv2
import numpy as np


@dataclass
class GetModel:
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class Detect:
    """
    Real-time emotion detection class 
    """
    def __init__(self,model):
        self.model_path = GetModel()
        self.model = model
        self.model.load_weights(os.path.join("artifacts","model.h5"))

    def display(self):
        try:

            logging.info("Detection initiated...")
            # prevents openCL usage and unnecessary logging messages
            cv2.ocl.setUseOpenCL(False)
        
            # dictionary which assigns each label an emotion (alphabetical order)
            emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
        
            # start the webcam feed
            cap = cv2.VideoCapture(0)
            emotion = ""
            if not cap.isOpened():
                print("Unable to open the camera")
                exit()
 
            timer = cv2.getTickCount() + 5 * cv2.getTickFrequency() 

            while True:
                # Find haar cascade to draw bounding box around face
                success, frame = cap.read()
                if not success:
                    break
                
                facecasc = cv2.CascadeClassifier('src/components/haarcascade_frontalface_default.xml')
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = facecasc.detectMultiScale(gray,scaleFactor=1.3, minNeighbors=5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)
                    roi_gray = gray[y:y + h, x:x + w]
                    cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
                    prediction = self.model.predict(cropped_img)
                    maxindex = int(np.argmax(prediction))
                    emotion = str(emotion_dict[maxindex])
                    cv2.putText(frame, emotion_dict[maxindex], (x+20, y-60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        
                # show the output frame
                cv2.imshow("FEM", frame)
                cv2.setWindowProperty("FEM", cv2.WND_PROP_TOPMOST, 1)
                cv2.moveWindow("FEM",500,200)
                key = cv2.waitKey(1) & 0xFF

                if cv2.getTickCount() > timer:
                    break
                
                if key == ord("q"):
                    break
        
            cap.release()
            cv2.destroyAllWindows()
            return emotion
        except Exception as e:
            logging.info("Error occured in detection")   
            raise CustomException(e,sys) 


