import os

class Config():
  RESULTS_CACHE_BASE_URL = os.environ.get('RESULTS_CACHE_BASE_URL', 'http://localhost:5002/')