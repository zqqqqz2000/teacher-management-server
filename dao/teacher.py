from global_var import db
from dao.department import Department 


class Teacher(db.Model):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(10), nullable=False)
    username = db.Column(db.String(10), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.Integer)
    education = db.Column(db.String(20))
    title = db.Column(db.String(10))
    marry = db.Column(db.Integer)
    did = db.Column(db.Integer, db.ForeignKey(Department.id))
    hiredate = db.Column(db.DateTime)
    status = db.Column(db.Integer)
