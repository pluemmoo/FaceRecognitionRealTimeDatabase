import cv2
import face_recognition
import pickle
import os

# Import the student images
folderPath = 'Images'
imgPathList = os.listdir(folderPath)
print(imgPathList)
imgList = []
studentIDs = []
for path in imgPathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    # print(os.path.splitext(path)[0])
    studentIDs.append(os.path.splitext(path)[0])
# print(len(imgList))
print(studentIDs)


def findEncodings(imageList):
    encodeList = []
    for img in imageList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img,  num_jitters=20)[0]
        encodeList.append(encode)

    return encodeList

print("Encoding started . . .")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIDs = [encodeListKnown, studentIDs]
print("Encoding Complete")


file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIDs, file)
file.close()
print("File Saved")

