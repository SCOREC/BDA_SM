#! /usr/bin/env python3

''' Dependenices to install via pip
      pip install requests '''

from multiprocessing import AuthenticationError
import requests
import json

''' You could opt to manually update the bearer token that you retreive from the Developer menu > GraphQL - Request Header token
      But be aware this is short-lived (you set the expiry, see Authenticator comments below) and you will need to handle
      expiry and renewal -- as shown below. As an alternative, you could start your life-cycle with authentication, or
      you could authenticate with each request (assuming bandwidth and latency aren't factors in your use-case). '''

class No_Request(Exception):
  def __init__(self, http_status_code, reason):
    self.http_status_code = http_status_code
    self.reason = reason

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

def get_bearer_token (auth_json):
  auth = auth_json["authenticator"]
  password = auth_json["password"]
  name = auth_json["name"]
  url = auth_json["url"]
  role = auth_json["role"]

  response = perform_graphql_request(f"""
    mutation authRequest {{
      authenticationRequest(
        input: {{authenticator: "{auth}", role: "{role}", userName: "{name}"}}
      ) {{
        jwtRequest {{
          challenge, message
        }}
      }}
    }}
  """, url = url) 
  jwt_request = response['data']['authenticationRequest']['jwtRequest']
  if jwt_request['challenge'] is None:
    raise AuthenticationError(jwt_request['message'])
  else:
      print("Challenge received: " + jwt_request['challenge'])
      response=perform_graphql_request(f"""
        mutation authValidation {{
          authenticationValidation(
            input: {{authenticator: "{auth}", signedChallenge: "{jwt_request["challenge"]}|{password}"}}
            ) {{
            jwtClaim
          }}
        }}
    """, url = url)

  try:
    jwt_claim = response['data']['authenticationValidation']['jwtClaim']
  except KeyError as err:
    raise AuthenticationError('Error getting JWT. Platform responded {}'.format(response))


  return f"Bearer {jwt_claim}"