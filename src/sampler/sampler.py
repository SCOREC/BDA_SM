from os import getenv
from server import app

if __name__ == '__main__':
  print("running from sampler.py")
  app.run(
    host=getenv('IP', '0.0.0.0'),
    port=int(getenv('SAMPLER_PORT', 5005)),
    debug=(getenv('SAMPLER_DEBUG', "False") == "True"),
  )