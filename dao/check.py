from global_var import db


class Check(db.Model):
    __tablename__ = 'check'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tid = db.Column(db.Integer, db.ForeignKey('teacher.id'))
    date = db.Column(db.Date)
    check = db.Column(db.Integer)
