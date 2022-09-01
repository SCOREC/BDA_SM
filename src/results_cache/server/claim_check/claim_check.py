from multiprocessing import AuthenticationError
from server import app
from os import getenv, getpid

import hashlib
import jwt
from datetime import datetime, timedelta

JWT_SECRET = str(datetime.now().timestamp) + str(getpid()) + getenv("RC_JWT_SALT", app.config['JWT_SALT'])

class ClaimCheck(object):
  def __init__(self, username: str, offset: int=0) -> None:
    self._username = username
    dtoffset = timedelta(seconds=offset)
    self._eta = str((datetime.now() + dtoffset).timestamp())
    self._token = ClaimCheck._encode_token(self._username, self._eta)
    self._shortname = ClaimCheck._encode_shortname(self._token)
  
  @classmethod
  def from_jwt(cls, token: str):
    payload = jwt.decode(token, key=JWT_SECRET, algorithms=app.config['JWT_ALGORITHM'])
    claim_check = cls(payload['username'])
    claim_check.set_eta(payload['eta'])
    return claim_check

  def set_eta(self, eta):
    self._eta = eta
    self._token = ClaimCheck._encode_token(self._username, self._eta)
    self._shortname = ClaimCheck._encode_shortname(self._token)

  @staticmethod
  def _encode_shortname(token: str) -> str:
    return hashlib.md5(token.encode()).hexdigest()

  @staticmethod
  def _encode_token(username, eta) -> str:
    payload = {"username": username, "eta": eta}
    return jwt.encode(payload=payload, key=JWT_SECRET, algorithm=app.config['JWT_ALGORITHM'])
  
  def is_valid(self, username) -> bool:
    if self.username != username:
      return False
    else:
      return True

  def validate_or_throw(self, username: str, exception):
    if not self.is_valid(username):
      raise exception("Username does not match ClaimCheck")
    return 

  def __str__(self) -> str:
    return self._token
  
  @property
  def username(self) -> str:
    return self._username
  
  @property
  def eta(self) -> str:
    return self._eta

  @property
  def token(self) -> str:
    return self._token
  
  @property
  def shortname(self) -> str:
    return self._shortname
  
