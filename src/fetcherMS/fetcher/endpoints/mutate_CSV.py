from .PythonGraphQLRequestSample import perform_graphql_request, get_bearer_token
from werkzeug.exceptions import abort, BadRequest
from .routes import set_CSV_TimeSeries_data
import requests

def do_query(smp_query):
  global current_bearer_token
  print("Requesting Data from CESMII Smart Manufacturing Platform...")
  print()

  ''' Request some data -- this is an equipment query.
        Use Graphiql on your instance to experiment with additional queries
        Or find additional samples at https://github.com/cesmii/API/blob/main/Docs/queries.md '''
#  smp_query = """
#    {
#      equipments {
#        id
#        displayName
#      }
#    }"""
  smp_response = ""

  try:
    #Try to request data with the current bearer token
    smp_response = perform_graphql_request(smp_query, headers={"Authorization": current_bearer_token})
  except requests.exceptions.HTTPError as e:
    # 403 Client Error: Forbidden for url: https://demo.cesmii.net/graphql
    #print(e)
    if "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
      print("Bearer Token expired!")
      print("Attempting to retreive a new GraphQL Bearer Token...")
      print()

      #Authenticate
      current_bearer_token = get_bearer_token()

      print("New Token received: " + current_bearer_token)
      print()

      #Re-try our data request, using the updated bearer token
      # TODO: This is a short-cut -- if this subsequent request fails, we'll crash. You should do a better job :-)
      smp_response = perform_graphql_request(smp_query, headers={"Authorization": current_bearer_token})
    else:
      print("An error occured accessing the SM Platform!")
      print(e)
      exit(-1)
    
  return smp_response

def mutate_CSV(auth_json, query_json, check_auth=True):
    if query_json:
        max_samples = query_json['max_samples']
        eq_ids = query_json['tag_ids']
        start_time = query_json['start_time']
        end_time = query_json['end_time']
    else:
        raise BadRequest('query_json object is None')
    column_id= None
    column_name="current"
    tagid=""
    startTime=""
    endTime=""
    mutation_string = set_CSV_TimeSeries_data(column_id, column_name, tagid, startTime, endTime )
    print(mutation_string + '\n')
    smp_response = do_query((str(mutation_string)))
    print("Response from SM Platform was...")
    print(json.dumps(smp_response, indent=2))
    