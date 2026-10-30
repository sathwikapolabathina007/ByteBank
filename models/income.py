from . import db

class Income(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    source = db.Column(db.String(100), nullable=False)

    amount = db.Column(db.Float, nullable=False)

    date = db.Column(db.String(20), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)