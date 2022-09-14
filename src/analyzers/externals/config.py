import os

class ExternalsConfig(object):
  fetcher_base_url = os.environ.get('FETCHER_BASE_URL', "http://localhost:5004")
  sampler_base_url = os.environ.get('SAMPLER_BASE_URL', "http://localhost:5005")
  sampler_url = sampler_base_url.rstrip(" /") + "/api/sample"
  sampler_array_url = sampler_base_url.rstrip(" /") + "/api/sampleArray"
