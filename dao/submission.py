from global_var import db


class Submission(db.Model):
    __tablename__ = 'submission'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tid = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    check_fine = db.Column(db.Float)
    basic_salary = db.Column(db.Float)
    bonus = db.Column(db.Float)
    tax = db.Column(db.Float)
    comment = db.Column(db.String(128))
    date = db.Column(db.Date)
    approve = db.Column(db.Integer, default=0)
