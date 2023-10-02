import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
from datetime import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://faceattendacerealtime-bc65f-default-rtdb.asia-southeast1.firebasedatabase.app/",
        "storageBucket": "faceattendacerealtime-bc65f.appspot.com",
    },
)

bucket = storage.bucket()

# webcam
cap = cv2.VideoCapture(0)
# ukuran layar webcam
cap.set(3, 640)
cap.set(4, 480)

# background
imgBackground = cv2.imread("resources/background.png")

# importing the mode images into a list
folderModePath = "resources/Modes"
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

# Load the encoding file
print("Loading Encode File...")
file = open("EncodeFile.p", "rb")
encodeListWithIds = pickle.load(file)
file.close()
encodeListKnown, employeeId = encodeListWithIds
# print(employeeId)
print("Encode File Loaded")


modeType = 0
counter = 0
id = -1
imgEmployee = []


while True:
    success, img = cap.read()

    imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

    faceCurrFrame = face_recognition.face_locations(imgSmall)
    encodeCurrFrame = face_recognition.face_encodings(imgSmall, faceCurrFrame)

    # letakkan webcam di background sesuai template
    imgBackground[162 : 162 + 480, 55 : 55 + 640] = img
    imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgModeList[modeType]

    if faceCurrFrame:
        for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("Matches", matches)
            # print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Match Index",matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print("Employee Id : ", employeeId[matchIndex])
                # bounding box
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                boundingbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, boundingbox, rt=0)
                id = employeeId[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

            if counter != 0:
                if counter == 1:
                    # download information
                    # get the data
                    employeeInfo = db.reference(f"Employee/{id}").get()
                    print(employeeInfo)

                    # Get the Image from the storage
                    blob = bucket.get_blob(f"images/{id}.png")
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgEmployee = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                    # update data of attendance
                    dateTimeObject = datetime.strptime(
                        employeeInfo["last_attendance_time"], "%Y-%m-%d %H:%M:%S"
                    )
                    secondsElapsed = (datetime.now() - dateTimeObject).total_seconds()
                    print(secondsElapsed)
                    if secondsElapsed > 30:
                        ref = db.reference(f"Employee/{id}")
                        employeeInfo["total_attendance"] += 1
                        ref.child("total_attendance").set(
                            employeeInfo["total_attendance"]
                        )
                        ref.child("last_attendance_time").set(
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgModeList[
                            modeType
                        ]

                if modeType != 3:
                    if 10 < counter < 20:
                        modeType = 2

                    imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgModeList[
                        modeType
                    ]

                    if counter <= 10:
                        cv2.putText(
                            imgBackground,
                            str(employeeInfo["total_attendance"]),
                            (861, 125),
                            cv2.FONT_HERSHEY_COMPLEX,
                            1,
                            (100, 100, 100),
                            1,
                        )

                        cv2.putText(
                            imgBackground,
                            str(employeeInfo["position"]),
                            (1006, 550),
                            cv2.FONT_HERSHEY_COMPLEX,
                            0.4,
                            (100, 100, 100),
                            1,
                        )

                        cv2.putText(
                            imgBackground,
                            str(id),
                            (1006, 493),
                            cv2.FONT_HERSHEY_COMPLEX,
                            0.4,
                            (100, 100, 100),
                            1,
                        )

                        cv2.putText(
                            imgBackground,
                            str(employeeInfo["standing"]),
                            (910, 625),
                            cv2.FONT_HERSHEY_COMPLEX,
                            0.4,
                            (100, 100, 100),
                            1,
                        )

                        cv2.putText(
                            imgBackground,
                            str(employeeInfo["year"]),
                            (1025, 625),
                            cv2.FONT_HERSHEY_COMPLEX,
                            0.4,
                            (100, 100, 100),
                            1,
                        )

                        cv2.putText(
                            imgBackground,
                            str(employeeInfo["starting_year"]),
                            (1125, 625),
                            cv2.FONT_HERSHEY_COMPLEX,
                            0.5,
                            (100, 100, 100),
                            1,
                        )

                        (w, h), _ = cv2.getTextSize(
                            employeeInfo["name"], cv2.FONT_HERSHEY_COMPLEX, 1, 1
                        )
                        offset = (414 - w) // 2
                        cv2.putText(
                            imgBackground,
                            str(employeeInfo["name"]),
                            (808 + offset, 445),
                            cv2.FONT_HERSHEY_COMPLEX,
                            1,
                            (100, 100, 100),
                            1,
                        )

                        imgBackground[175 : 175 + 216, 909 : 909 + 216] = imgEmployee

                    counter += 1

                    if counter >= 20:
                        counter = 0
                        modeType = 0
                        employeeInfo = []
                        imgEmployee = []
                        imgBackground[44 : 44 + 633, 808 : 808 + 414] = imgModeList[
                            modeType
                        ]
    else:
        modeType = 0
        counter = 0

    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
