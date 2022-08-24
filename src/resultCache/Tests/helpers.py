import random
import string
from Tests.base import app
import server.file_daemon
import server.claim_check as cc

config = app.config

def get_test_set():
  usernames = generate_string(config['STRING_LEN_TEST'], config['NUM_USERS_TEST'])
  ccs = [cc.ClaimCheck(s).shortname for s in generate_string(config['STRING_LEN_TEST'], config['NUM_CC_TEST'])]
  data = generate_string(config['NUM_CHARACTERS_DATA_TEST'], config['NUM_DATA_FILES'])
  return usernames, ccs, data

def generate_string(l, n):
  strings = []
  for _ in range(n):
    gen_string = ''.join(random.choice(string.ascii_letters) for _ in range(l))
    strings.append(gen_string)
  return strings

def bring_up_file_handler():
  if server.file_daemon.file_handler is None:
    server.file_daemon.file_handler = server.file_daemon.FileHandler(
      app.config['MIN_EXPIRY_TIME'], app.config['MAX_EXPIRY_TIME'],
      app.config['RATE_AVERAGE_WINDOW'], app.config['DIRECTORY']
      )
    pass

def shut_down_file_handler():
  if server.file_daemon.file_handler is not None:
    server.file_daemon.file_handler.delete_all(True)
    server.file_daemon.file_handler.end()