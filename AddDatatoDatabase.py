import firebase_admin
from firebase_admin import credentials, db, storage
from EncodeGenerator import folderPath, imgPathList


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-3fa7b-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "faceattendancerealtime-3fa7b.appspot.com"
})

ref = db.reference('Students')

data = {
    '2021326660023':
        {
            "name": "Chaiwat Plongkaew",
            "major": "Software Engineering",
            "starting_year": 2021,
            "total_attendance": 3,
            "year": 3,
            "last_attendance_time": "2023-12-1 14:50:54",
            "final_exam_status": ""
        },
    '2022218880021':
        {
            "name": "Emily Johnson",
            "major": "Computer Science",
            "starting_year": 2022,
            "total_attendance": 2,
            "year": 2,
            "last_attendance_time": "2023-12-15 09:20:12",
            "final_exam_status": ""
        },
    '2022157890123':
        {
            "name": "Elon musk",
            "major": "Electrical Engineering",
            "starting_year": 2022,
            "total_attendance": 4,
            "year": 2,
            "last_attendance_time": "2023-12-12 16:15:47",
            "final_exam_status": ""
        },
    '2023309990056':
        {
            "name": "Saowani Sriyaphai",
            "major": "Mechanical Engineering",
            "starting_year": 2023,
            "total_attendance": 1,
            "year": 1,
            "last_attendance_time": "2023-12-10 11:45:32",
            "final_exam_status": ""
        },
    '2024157770042':
        {
            "name": "Sarah Davis",
            "major": "Civil Engineering",
            "starting_year": 2024,
            "total_attendance": 3,
            "year": 1,
            "last_attendance_time": "2023-12-9 13:25:09",
            "final_exam_status": ""
        },
    '2021326660024':
        {
            "name": "Lauron John Albert",
            "major": "Software Engineering",
            "starting_year": 2021,
            "total_attendance": 11,
            "year": 3,
            "last_attendance_time": "2023-12-9 13:25:09",
            "final_exam_status": ""
        }

}

for path in imgPathList:
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


for key, value in data.items():
    ref.child(key).set(value)