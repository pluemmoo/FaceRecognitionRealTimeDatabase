import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import datetime


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-3fa7b-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "faceattendancerealtime-3fa7b.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 480)
cap.set(4, 640)

imgBackground = cv2.imread('Resources1/background.png')

# Import modes to the list
folderModePath = 'Resources1/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# print(len(imgModeList))

# load the encoding file
print("Loading Encode File ...")
file = open("EncodeFile.p", "rb")
encodeListKnownWithIDs = pickle.load(file)
file.close()
encodeListKnown, studentIDs = encodeListKnownWithIDs
print(studentIDs)
print("Encode File Loaded")


modeType = 0
counter = 0
id = -1
imgStudent = []


while True:
    success, img = cap.read()

    img = img[94:480, 165:490]

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # set video margin
    imgBackground[222:222+386, 261:261+325] = img  # height width
    imgBackground[222:222 + 381, 626:626 + 407] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace, tolerance=0.45)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches: ", matches)
            # print("faceDis: ", faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Match Index: ", matchIndex)

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 265 + x1, 226 + y1, (x2 - 8) - x1, (y2 - 6 ) - y1

            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

            if matches[matchIndex]:
                print("known Face Detected")
                print(studentIDs[matchIndex])

                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0, colorC=(0, 0, 255))
                id = studentIDs[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                # Get the Data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo['total_attendance'])
                # Get the Image from the storage
                file_extensions = ['.png', '.jpg']
                blob = None
                for extension in file_extensions:
                    blob = bucket.get_blob(f'Images/{id}{extension}')
                    if blob is not None:
                        break
                if blob is not None:
                    ref = db.reference(f'Students/{id}')
                    # if total attendance below 12 not verify
                    if studentInfo['total_attendance'] >= 12:
                        studentInfo['final_exam_status'] = "Verify"
                        ref.child('final_exam_status').set(studentInfo['final_exam_status'])

                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                    # Update data of attendance
                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                      "%Y-%m-%d %H:%M:%S")
                    secondElapsed = (datetime.now() - datetimeObject).total_seconds()
                    print(secondElapsed)
                    if secondElapsed > 30:
                        studentInfo['total_attendance'] += 1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[222:222 + 381, 626:626 + 407] = imgModeList[modeType]

            if modeType != 3:

                if 20 < counter < 30:
                    modeType = 2

                imgBackground[222:222 + 381, 626:626 + 407] = imgModeList[modeType]

                if counter <= 20:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (626+43, 222+83),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (626+143, 222+327),
                                cv2.FONT_HERSHEY_COMPLEX, 0.4, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(id), (626+123, 222+279),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (626 + 342, 222 + 106),
                                cv2.FONT_HERSHEY_COMPLEX, 0.4, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['final_exam_status']), (626 + 342, 222 + 161),
                                cv2.FONT_HERSHEY_COMPLEX, 0.3, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (626+342, 222+212),
                                cv2.FONT_HERSHEY_COMPLEX, 0.4, (100, 100, 100), 1)

                    # (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    # offset = (414 - w) // 2
                    # cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                    #             cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                    imgBackground[264:264+196, 746:746+167] = imgStudent

                counter += 1

                if counter >= 30:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []

                    imgBackground[222:222 + 381, 626:626 + 407] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
