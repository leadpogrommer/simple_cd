from flask_bcrypt import generate_password_hash, check_password_hash

from database.db import db


class User(db.Document):
    username = db.StringField(unique=True, required=True)
    password = db.BinaryField(required=True)

    def set_password(self, pwd: str):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd: str) -> bool:
        return check_password_hash(self.password, pwd)


class Project(db.Document):
    repo = db.URLField(required=True)
    branch = db.StringField(required=True)
    creator = db.ReferenceField(User)
    command = db.StringField(rquired=True)
    logs = db.StringField(default='')

    locked = db.BooleanField(default=True)

    def unlock(self):
        self.locked = False
        self.save()
