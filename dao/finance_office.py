from global_var import db


class FinanceOffice(db.Model):
    __tablename__ = 'finance_office'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(128), nullable=False)
