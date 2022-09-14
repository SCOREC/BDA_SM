import requests
from externals.config import ExternalsConfig as config
from externals.exceptions import ConnectionException


def query_fetcher_ts(query: str, auth : str) -> str:
  params = {
      "as_csv" : "False",
      "as_json": "True",
      "query": query,
      "auth" : auth
  }
  full_url = "{}/api/timeseriesArrayById".format(config.fetcher_base_url.rstrip('/ '))
  resp = requests.get(full_url, params=params)
  if resp.status_code != 200:
    raise Exception("Fetcher connection issues")

  return resp.text

def query_fetcher_ls(query: str, auth : str) -> str:
  params = {
      "as_csv" : "False",
      "as_json": "True",
      "query": query,
      "auth" : auth
  }
  full_url = "{}/api/getLotSeries".format(config.fetcher_base_url.rstrip('/ '))
  resp = requests.get(full_url, params=params)
  if resp.status_code != 200:
    raise Exception("Fetcher connection issues")

  return resp.text