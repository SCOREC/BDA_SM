from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from server import db, app
from server.errors import AuthenticationError
from server.Logger.models import Event


def nowPlusLifetime():
    return datetime.utcnow() + timedelta(seconds=app.config.get('JWT_LIFETIME'))

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    access_list = db.Column(db.PickleType)
    auth_token = db.relationship('AuthToken', backref='owner')

    def __init__(self, username=None, email=None, password=None, access_list=None):
      self.username = username
      self.email = email
      if password is not None:
          self.set_password(password)
      else:
          password_hash = "***"
      
      if access_list is not None:
          self.access_list = access_list
      else:
          self.access_list = list()
      
      ev = Event('USERS', 'Created user: {} with access: {}'.format(self.username,self.access_list))
      db.session.add(ev)
      db.session.commit()

    def __repr__(self):
        return '<User {}>\n'.format(self.username)    

    def set_authToken(self, token):
        self.auth_token = token

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        db.session.commit()

    def set_access_list(self, access_list):
        for access in access_list:
          if access not in app.config.get('ADMIN_ACL'):
            raise ValueError("No such access as {}".format(access))
        self.access_list = access_list

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_access_list(self, access_list):
        for permission in access_list:
            if permission not in self.access_list:
                return False
        else:
            return True
    
    def delete(self):
      user_id = self.id
      username = self.username
      ev = Event("USER", 'Deleted user "{}", id {}'.format(username, user_id) )
      AuthToken.query.filter_by(user_id=self.id).delete()
      db.session.delete(self)
      db.session.commit()


class AuthToken(db.Model):
    __tablename__ = 'authtokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    expiration_date = db.Column(db.DateTime, index=True, default=nowPlusLifetime)
    
    def __init__(self, user, refresh_token=None, password=None):
        if user is None:
          raise ValueError("User not specified")

        self.user_id = user.id
        if refresh_token is not None:
            if not refresh_token.isWellFormed or refresh_token.user_id != user.id:
              raise AuthenticationError("Invalid refresh token for user {}. Will not issue AuthToken.".format(user))

        elif password is not None:
            if not user.check_password(password):
              raise AuthenticationError("Bad password.")
        else:
            raise AuthenticationError("Invalid arguments to create AuthToken {}, {}, {}"
                                      .format(user,refresh_token,password))
        
        db.session.add(self)
        db.session.commit()
        return
    
    @classmethod
    def decode_jwt(cls, token):
      try:
        data = jwt.decode(token,
                          app.config.get('JWT_SECRET'),
                          app.config.get('JWT_ALGORITHM') 
                          )
        username = data['username']
        expiration_date = datetime.fromtimestamp(data['expiration_date'])
      except:
        raise ValueError("invalid JWT")
      
      return (username, expiration_date)

    @classmethod
    def jwt_is_expired(cls, token):
      (_, expiration_date) = AuthToken.decode_jwt(token)
      if expiration_date>datetime.utcnow():
        return False
      else:
        return True

    @classmethod
    def jwt_to_access_list(cls, token):
      try:
        data = jwt.decode(token,
                          app.config.get('JWT_SECRET'),
                          app.config.get('JWT_ALGORITHM') 
                          )
        username = data['username']
        expiration_date = datetime.fromtimestamp(data['expiration_date'])
      except Exception as err:
        raise AuthenticationError("Invalid JWT")
      
      if expiration_date<datetime.utcnow():
        raise AuthenticationError("Expired JWT")

      user = User.query.filter_by(username=username).first()
      return (username, user.access_list)
          

    @property
    def payload(self):
      user = User.query.get(self.user_id)

      return jwt.encode({'username': user.username, 
                         'expiration_date': self.expiration_date.timestamp()},
                         app.config.get('JWT_SECRET'),
                         app.config.get('JWT_ALGORITHM'))

    @property
    def isExpired(self):
      return self.expiration_date > datetime.utcnow()

    def __repr__(self):
        return '<Id: {}>, <User id: {}>\n  '.format(id, self.user_id)
    
    @classmethod
    def purge_expired(cls, date=None):

        if date is None:
            date = datetime.utcnow()

        AuthToken.query.filter(AuthToken.expiration_date<date).delete()
        db.session.commit()
        return
    
    def purge_user(id):
      AuthToken.query.filter(AuthToken.user_id == id).delete()
      db.session.commit()

class RefreshToken(db.Model):
    __tablename__ = 'refreshtokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payload = db.Column(db.String(256), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    expiration_date = db.Column(db.DateTime, index=True, default=nowPlusLifetime)

    def __repr__(self):
        return '<Id: {}>, <User id: {}>\n  payload: {}\n  expiration {}\n' \
          .format(self.id, self.user_id, self.payload, self.expiration_date)

    def __init__(self, user=None, encoded_payload=None):
        if encoded_payload is not None:
            if user is not None:
                raise ValueError("Cannot specify both a payload to work from and a user")

            try:
                payload = jwt.decode(encoded_payload,
                                    app.config.get('JWT_SECRET'),
                                    app.config.get('JWT_ALGORITHM'))
            except:
                raise AuthenticationError("Invalid could not decrypt refresh_token")

            user_id = payload['user_id']
            try:
                user = User.query.get(self.user_id)
            except:
                raise AuthenticationError("Could not find user of RefreshToken")

            

        self.user_id = user.id

        payload = { 
            'user_id': self.user_id,
            'expiration_date': nowPlusLifetime().timestamp()
            #'expiration_date': '{}'.format(nowPlusLifetime().isoformat())
        }
        self.payload = jwt.encode(payload, 
                                  app.config.get('JWT_SECRET'),
                                  app.config.get('JWT_ALGORITHM'))

        db.session.add(self)
        db.session.commit()
        return

    def purge_user(id):
      RefreshToken.query.filter(RefreshToken.user_id == id).delete()
      db.session.commit()

    @classmethod
    def purge_expired(cls, date=None):

        if date is None:
            date = datetime.utcnow()

        RefreshToken.query.filter(RefreshToken.expiration_date<date).delete()
        db.session.commit()
        return

    @property
    def isExpired(self):
      return self.expiration_date > datetime.utcnow()

    def isWellFormed(self):
      user =  User.query.get(self.user_id).first()

      if user is None:
          return False

      try:
          payload = jwt.decode(self.payload,
                              app.config.get('JWT_SECRET'),
                              app.config.get('JWT_ALGORITHM'))
      except:
          return False
      
      if payload['user_id'] != self.user_id:
        return False

      # Everything looks internally consistent
      return True