from app import db
from config import JWT_LIFETIME, JWT_SECRET, JWT_ALGORITHM
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from errors import AuthenticationError
import jwt

def nowPlusLifetime():
    return datetime.utcnow() + timedelta(seconds=JWT_LIFETIME)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    access_list = db.Column(db.PickleType)
    auth_tokens = db.relationship('AuthToken', backref='owner')
    #refresh_tokens = db.relationship('RefreshToken', backref='owner')

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

    def __repr__(self):
        return '<User {}>\n'.format(self.username)    

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_access_list(self, access_list):
        for permission in access_list:
            if permission not in self.access_list:
                return False
        else:
            return True
    
    def delete(self):
        AuthToken.query.filter_by(user_id=self.id).delete()
        db.session.delete(self)
        db.session.commit()


class AuthToken(db.Model):
    __tablename__ = 'authtokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    access_list = db.Column(db.PickleType)
    expiration_date = db.Column(db.DateTime, index=True, default=nowPlusLifetime)
    
    def __init__(self, user, refresh_token=None, access_list=None, password=None):
        self.user_id = user.id
        if refresh_token is not None:
            if refresh_token.isValid and refresh_token.user_id == user.id:
                self.access_list = refresh_token.access_list
            else:
                raise AuthenticationError("Invalid refresh token for user {}. Will not issue AuthToken.".format(user))

        elif password is not None and access_list is not None:
            if user.check_password(password):
                if not user.check_access_list(access_list):
                    raise AuthenticationError("Requested access list not allowed for this user. No AuthToken issued.")
                self.access_list = access_list
            else:
                raise AuthenticationError("Bad password.")
        else:
            raise AuthenticationError("Invalid arguments to create AuthToken {}, {}, {}, {}".format(user,access_list,refresh_token,password))
        
        db.session.add(self)
        db.session.commit()
        return
    
    def jwt_to_authToken(jwt):
        try:
            data = jwt.decode(jwt, JWT_SECRET, JWT_ALGORITHM) 
            username = data['username']
            access_list = data['access_list']
            expiration_date = data['expiration_date']
        except e:
            raise AuthenticationError("Invalid JWT")

        user = User.query.get(self.user_id)
        
        
        return (username, access_list, expiration_date)

    @property
    def payload(self):
        user = User.query.get(self.user_id)

        return jwt.encode({'username': user.username, 
                           'access_list': self.access_list,
                           'expiration_date': str(self.expiration_date)},
                           JWT_SECRET, JWT_ALGORITHM)

    def __repr__(self):
        #return '<Id: {}>, <User: {}>, <Expires: {}>\n  access_list: {}'.format(id, self.user, self.expiration_date, self.access_list)
        return '<Id: {}>, <User id: {}>\n  access_list: {}\n'.format(id, self.user_id, self.access_list)

    @classmethod
    def purge_expired(cls, date=None):

        if date is None:
            date = datetime.utcnow()

        AuthToken.query.filter(AuthToken.expiration_date<date).delete()
        db.session.commit()
        return

class RefreshToken(db.Model):
    __tablename__ = 'refreshtokens'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payload = db.Column(db.String(256), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    access_list = db.Column(db.PickleType)

    def __repr__(self):
        return '<Id: {}>, <User id: {}>\n  payload: {}\n'.format(self.id, self.user_id, self.payload)

    def __init__(self, user=None, access_list=None, encoded_payload=None):
        if encoded_payload is not None:
            if user is not None or access_list is not None:
                raise ValueError("Cannot specify both refresh_token and user/access_list pair")

            try:
                payload = jwt.decode(encoded_payload, JWT_SECRET, JWT_ALGORITHM)
            except:
                raise AuthenticationError("Invalid could not decrypt refresh_token")

            user_id = payload['user_id']
            try:
                user = User.query.get(self.user_id)
            except:
                raise AuthenticationError("Could not find user of RefreshToken")

            access_list = payload['access_list']
            

        self.user_id = user.id
        if user.check_access_list(access_list):
            self.access_list = access_list
        else:
            raise("Requested access list not allowed for this user. No RefreshToken issued")

        payload = { 
            'user_id': self.user_id,
            'access_list': self.access_list
        }
        self.payload = jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)

        db.session.add(self)
        db.session.commit()
        return


    def isValid(self):
        user_goldstandard = User.query.get(self.user_id)
        if not user_goldstandard.check_access_list(self.access_list):
            return False
        try:
            payload = jwt.decode(self.payload, JWT_SECRET, JWT_ALGORITHM)
        except:
            return False
        
        return True