from os import getenv
from server import app

if __name__ == '__main__':
  app.run(
    host=getenv('IP', '0.0.0.0'),
    port=getenv('FETCHER_PORT', 5000),
    debug=getenv('FETCHER_DEBUG', False),
  )