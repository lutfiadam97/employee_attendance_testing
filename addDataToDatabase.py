import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://faceattendacerealtime-bc65f-default-rtdb.asia-southeast1.firebasedatabase.app/"
    },
)

ref = db.reference("Employee")

data = {
    "1": {
        "name": "Lutfi Adam",
        "position": "Data Scientist",
        "total_attendance": 7,
        "starting_year": 2022,
        "standing": "Good",
        "year": 2,
        "last_attendance_time": "2022-12-11 00:54:34",
    },
    "2": {
        "name": "Bill Gates",
        "position": "CEO Microsoft",
        "total_attendance": 12,
        "starting_year": 2019,
        "standing": "Good",
        "year": 2,
        "last_attendance_time": "2022-12-01 00:54:34",
    },
    "3": {
        "name": "Cristian Ronaldo",
        "position": "Football Player",
        "total_attendance": 14,
        "starting_year": 2021,
        "standing": "Good",
        "year": 9,
        "last_attendance_time": "2022-12-02 00:54:34",
    },
    "4": {
        "name": "Elon Musk",
        "position": "CEO of Tesla",
        "total_attendance": 2,
        "starting_year": 2012,
        "standing": "Good",
        "year": 5,
        "last_attendance_time": "2022-12-11 00:54:34",
    },
}

for key, value in data.items():
    ref.child(key).set(value)
