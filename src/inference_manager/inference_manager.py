from os import getenv
from server import app

if __name__ == '__main__':
  app.run(
    host=getenv('IP', '0.0.0.0'),
    port=int(getenv('INFERENCE_MANAGER_PORT', 5003)),
    debug=(getenv('INFERENCE_MANAGER_DEBUG', "False") == "True"),
  )