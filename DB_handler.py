import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

class DBModule:
    def __init__(self):
        cred = credentials.Certificate("nsbs-first-firebase-adminsdk-z4rr4-ae523c4d88.json")
        firebase_admin.initialize_app(cred, {'databaseURL':'https://nsbs-first-default-rtdb.firebaseio.com/'})

        self.dir = db.reference()


    def login(self, id, pwd):
        pass

    def signin_verification(self, uid):
        users = self.dir.child("users").get()
        for user_id, user_info in users.items():
            if uid == user_id:
                return False
            
        return True

    def signin(self, _id_, pwd, name, email):
        information = {
            "pwd": pwd,
            "name": name,
            "email": email
        }
        print(information)
        if self.signin_verification(_id_):
            self.dir.child("users").child(_id_).update(information)
            return True
        else:
            return False

        pass

    def write_post(self, user, contents):
        pass

    def post_list(self):
        pass

    def post_detail(self, pid):
        pass

    def get_user(self, uid):
        pass