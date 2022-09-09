import os

class ExternalsConfig(object):
  fetcher_base_url = os.environ.get('FETCHER_BASE_URL', "http://localhost:5004")
  sampler_url = os.environ.get('SAMPLER_URL', "http://localhost:5005/api/sample")