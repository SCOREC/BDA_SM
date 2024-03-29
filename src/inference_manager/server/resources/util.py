from flask import request
from flask.wrappers import Response
import requests

def forward_request(target_url,*args, **kwargs):

   if len(request.args) > 0:
      params = request.args
   else:
      params = {}

   try:
      print("Forwarding Request to : {}".format(target_url))
      resp = requests.request(
         method=request.method,
         url=target_url,
         headers={key: value for (key, value) in request.headers if key != 'Host'},
         params=params,
         data=request.get_data(),
         cookies=request.cookies,
         allow_redirects=False)

      excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
      headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

      response = Response(resp.content, resp.status_code, headers)
   except Exception as e:
      response = Response("Server unavailable", status=404)

   return response
