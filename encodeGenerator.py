import cv2
import face_recognition
import pickle
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://faceattendacerealtime-bc65f-default-rtdb.asia-southeast1.firebasedatabase.app/",
        'storageBucket': "faceattendacerealtime-bc65f.appspot.com"
    }
)

# importing employee images
folderPath = "images"
PathList = os.listdir(folderPath)
# print(PathList)
imgList = []
employeeId = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    employeeId.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


    # print(os.path.splitext(path)[0])
print(employeeId)


def findEncodings(imagesList):
    encodeList = []
    # change the color from bgr to rgb
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList


print("Encoding Started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, employeeId]
# print(encodeListKnown)
print("Encoding Complete!")

# save pickle file
file = open("EncodeFile.p", "wb")
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
