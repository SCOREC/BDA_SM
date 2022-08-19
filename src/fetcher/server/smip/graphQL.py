import requests
import json
import pandas as pd
import server.smip.queries as queries
from server.smip import formatters as fm

class No_Request(Exception):
  def __init__(self, http_status_code, reason):
    self.http_status_code = http_status_code
    self.reason = reason

class AuthenticationError(Exception):
    def __init__(self, message):
        self.message = message

def perform_graphql_request(content, url, headers=None):
  try:
    r = requests.post(url=url, headers=headers, data={"query": content})
  except requests.RequestException as err:
    raise No_Request(-1,err)
  r.raise_for_status()
  if r.ok:
    return r.json()
  else:
    raise No_Request(r.status_code, r.reason)

def get_bearer_token (url, username, role, password):

  query = queries.bearer_token.format(username=username, role=role)
  response = perform_graphql_request(query, url=url)

  jwt_request = response['data']['authenticationRequest']['jwtRequest']
  if jwt_request['challenge'] is None:
    raise AuthenticationError(jwt_request['message'])
  else:
      query = queries.challenge_response.format(username=username,
        challenge=jwt_request['challenge'],
        password=password)
      response=perform_graphql_request(query, url=url)

  try:
    jwt_claim = response['data']['authenticationValidation']['jwtClaim']
  except KeyError as err:
    raise AuthenticationError('Error getting JWT. Platform responded {}'.format(response))

  return jwt_claim


def get_equipment_description(url, token, attrib_id):

  query = queries.attrib_by_id.format(attrib_id=attrib_id)
  
  try:
    smp_response = perform_graphql_request(query,
      url,
      headers={"Authorization": f"Bearer {token}"}
    )
    return smp_response['data']
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)

def get_raw_attribute_data( url, token, attrib_id):
  query_template = queries.get_raw_attribute_data
  (start_time, end_time) = fm.max_time_range()
  query = query_template.format(attrib_id=attrib_id, start_time=start_time, end_time=end_time)
  try:
    smp_response = perform_graphql_request(query, url, headers={"Authorization": f"Bearer {token}"})
  except Exception as err:
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)

  df = fm.json_timeseries_to_table(smp_response['data']['attribute']['getTimeSeries'], attrib_id=attrib_id)
  return df.to_csv(index=False)

def get_timeseries(url, token, attrib_id, start_time, end_time, max_samples):

  start_time_long_ago, end_time_far_future = fm.max_time_range()
  if start_time == None: start_time = start_time_long_ago
  if end_time == None: end_time = end_time_far_future
  if start_time.lower() == "now": start_time = fm.now()

  query_template = queries.get_timeseries
  query = query_template.format(index=1, attrib_id=attrib_id,
    start_time=start_time, end_time=end_time, max_samples=max_samples)
  
  try:
    smp_response = perform_graphql_request(query, url,  headers={"Authorization": f"Bearer {token}"})
  except Exception as err:
    print("get_time_series error:", err)
    if "forbidden" in str(err).lower() or "unauthorized" in str(err).lower():
      raise(AuthenticationError(err))
    else:
      raise(err)
    print(smp_response)
  
  dataframe = fm.json_timeseries_to_table(smp_response['data']['getRawHistoryDataWithSampling'], attrib_id=attrib_id)
  return dataframe.to_csv(index=False)

def get_timeseries_array(url, token, attrib_id_list,
  start_time, end_time, period, max_samples=0 ):
  dataframes = []
  for attrib_id in attrib_id_list:
    dataframes.append(get_timeseries(url, token, attrib_id, start_time, end_time, max_samples))
  
  csv = fm.combine_dataframes(dataframes, period).to_csv(index=False)
  return csv
