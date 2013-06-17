from shiftexchange import db
from sqlalchemy.orm import relationship, backref
from werkzeug import generate_password_hash, check_password_hash
from flask_login import current_user

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String)
    name = db.Column(db.String)
  
    def __init__(self, email, password, name):
        self.email = email
        self.password = generate_password_hash(password)
        self.name = name

    def __repr__(self):
        return '<name %r>' % self.name

    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)

    def get_id(self):
        return unicode(self.id)

    def is_active(self):
        #return self._user.enabled
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True


class Shift(db.Model):
    __tablename__ = 'shifts'
    id = db.Column(db.Integer, primary_key=True)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    poster = relationship('User', backref=backref('shifts_posted'), primaryjoin = "Shift.poster_id == User.id")
    claimer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    claimer = relationship('User', backref=backref('shifts_claimed'), primaryjoin = "Shift.claimer_id == User.id")
    claimable = db.Column(db.Boolean)
    time = db.Column(db.String)
    employer = db.Column(db.String)

    def __init__(self, poster_id, time, employer):
        self.poster_id = poster_id
        self.claimer = None
        self.claimable = True
        self.time = time
        self.employer = employer

    def __repr__(self):
        return '<Shift %r>' % self.id



from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqlamodel import ModelView
from shiftexchange import app


## ADMIN ##
class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.email == "lhh@admin"

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Shift, db.session))
## /ADMIN ##