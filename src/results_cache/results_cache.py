from os import getenv
from server import app

if __name__ == '__main__':
  app.run(
    host=getenv('IP', '0.0.0.0'),
    port=int(getenv('RESULTS_CACHE_PORT', 5002)),
    debug=(getenv('RESULTS_CACHE_DEBUG', "False") == "True"),
  )