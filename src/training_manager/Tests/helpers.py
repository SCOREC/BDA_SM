import json, re
from multiprocessing import AuthenticationError
from Tests import Config, TrainerConfig
import requests
from base64 import b64decode, b64encode

def redeem_claim_check(username : str, claim_check : str):
  url = TrainerConfig.RESULTS_CACHE_BASE_URL.rstrip("/ ") + "/api/get_result"
  data = {"username" : username}
  data['claim_check'] = claim_check
  response = requests.get(url, params=data)
  return json.loads(response.content)['contents']

def get_claim_check_status(username : str, claim_check : str):
  url = TrainerConfig.RESULTS_CACHE_BASE_URL.rstrip("/ ") + "/api/get_status"
  data = {"username" : username}
  data['claim_check'] = claim_check
  response = requests.get(url, params=data)
  return json.loads(response.content)


def decode_base64(data, altchars=b'+/'):
  data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)  # normalize
  missing_padding = len(data) % 4
  if missing_padding:
    data += b'='* (4 - missing_padding)
  return b64decode(data, altchars)

def json_from_mko_string(string):
  json_string = (decode_base64(bytes(string, "utf-8")).decode("utf-8"))
  return json.loads(json_string)

def perform_graphql_request(content, url, headers=None):
  try:
    r = requests.post(url=url, headers=headers, data={"query": content})
  except requests.RequestException as err:
    raise AuthenticationError(-1,err)
  r.raise_for_status()
  if r.ok:
    return r.json()
  else:
    raise AuthenticationError(r.status_code, r.reason)

def get_bearer_token (url, username, role, password):

  bearer_token_template = '''
    mutation authRequest {{
      authenticationRequest(
        input: {{authenticator: "{username}", role: "{role}", userName: "{username}"}})
        {{
          jwtRequest {{
            challenge, message
        }}
      }}
    }}
    '''

  challenge_response_template = '''
    mutation authValidation {{
      authenticationValidation(
        input: {{authenticator: "{username}",
        signedChallenge: "{challenge}|{password}"}}
        ) {{
          jwtClaim
          }}
        }}
    '''

  query = bearer_token_template.format(username=username, role=role)
  response = perform_graphql_request(query, url=url)

  jwt_request = response['data']['authenticationRequest']['jwtRequest']
  if jwt_request['challenge'] is None:
    raise AuthenticationError(jwt_request['message'])
  else:
      query = challenge_response_template.format(username=username,
        challenge=jwt_request['challenge'],
        password=password)
      response=perform_graphql_request(query, url=url)

  try:
    jwt_claim = response['data']['authenticationValidation']['jwtClaim']
  except KeyError as err:
    raise AuthenticationError('Error getting JWT. Platform responded {}'.format(response))

  return jwt_claim