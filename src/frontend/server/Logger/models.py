from server import db, app
from datetime import datetime, timedelta

class Event(db.Model):
  __bind_key__ = 'log'
  __tablename__ = 'events'
  id = db.Column(db.Integer, primary_key=True)
  datestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

  kind = db.Column(db.String(8), index=True)
  message = db.Column(db.String(128))

  def __init__(self, kind, message):
    self.kind = kind
    self.message = message
  
  def logit(self):
    db.session.add(self)
    db.session.commit()

  def __repr__(self):
    return "id: {}, date: {}, kind: {}\n   message: {}".\
          format(self.id, self.datestamp.isoformat(), self.kind, self.message)
  
  def __str__(self):
    return "{}: {}".format(self.kind, self.message)