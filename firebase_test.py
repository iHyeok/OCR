import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("nsbs-first-firebase-adminsdk-z4rr4-ae523c4d88.json")
firebase_admin.initialize_app(cred, {'databaseURL':'https://nsbs-first-default-rtdb.firebaseio.com/'})

dir = db.reference()
dir.update({"자동차":"기아"})