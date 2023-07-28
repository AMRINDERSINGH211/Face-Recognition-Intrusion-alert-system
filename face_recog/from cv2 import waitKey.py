from cv2 import waitKey
import face_recognition
import cv2
import numpy as np
import os
from datetime import datetime
import smtplib
import ssl
from win32com.client import Dispatch
import traceback
import pywhatkit as pwt
import time as time

path = 'ImagesAttendance'
images = []     # LIST CONTAINING ALL THE IMAGES
className = []    # LIST CONTAINING ALL THE CORRESPONDING CLASS Names
myList = os.listdir(path)
print("Total Classes Detected:",len(myList))

for x,cl in enumerate(myList):
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    className.append(os.path.splitext(cl)[0])

def speak(str):
    speak = Dispatch(("SAPI.SpVoice"))
    speak.Speak(str)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

def markAttendance(name):
    with open('Attendance.csv','r+') as f:
        myDataList = f.readlines()
        nameList =[]
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in  nameList:
            now = datetime.now()
            dt_string = now.strftime("%H:%M:%S")
            f.writelines(f'{name},{dt_string} \n')


encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap =cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    
    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        print(faceDis)
        matchIndex = np.argmin(faceDis)

        if faceDis[matchIndex]<0.50:
            print(faceDis[matchIndex])
            name = className[matchIndex].upper()
        else: 
            name = "Unknown"
            pwt.sendwhatmsg("+9195825xxxxxs", "UNKNOWN PERSON ENTERED", int(time.strftime("%H")),int(time.strftime(("%M"))) + 1)
            print("msg sent")
        print(name)
        #markAttendance(name)
        
        y1,x2,y2,x1=faceLoc
        y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)
            
    cv2.imshow('Webcam',img)
    cv2.waitKey(1)
