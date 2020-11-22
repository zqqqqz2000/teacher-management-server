from global_var import db


class Salary(db.Model):
    __tablename__ = 'salary'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tid = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    check_fine = db.Column(db.Float)
    basic_salary = db.Column(db.Float)
    bonus = db.Column(db.Float)
    tax = db.Column(db.Float)
    date = db.Column(db.Date)
    comment = db.Column(db.String(128))
