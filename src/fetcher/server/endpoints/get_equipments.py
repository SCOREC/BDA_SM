from .PythonGraphQLRequestSample import perform_graphql_request, get_bearer_token
from werkzeug.exceptions import abort, BadRequest

'''
Grabbing all the equipment

'''

def Perform_getEquipments(auth_json, check_auth=True):
    
    print("Requesting Data from CESMII Smart Manufacturing Platform...")

    smp_query = """query {
            equipments {
                displayName,
                id
            }
    }"""
    smp_response = ""

    # Get the first bearer token
    if auth_json:
        current_bearer_token = get_bearer_token(auth_json)
    else:
        raise BadRequest('auth_json object is None')
    try:
        # Try to request data with the current bearer token
        print(smp_query)
        smp_response = perform_graphql_request(smp_query, auth_json["url"],  headers={"Authorization": current_bearer_token})
    except Exception as e:
        if "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
            print("Bearer Token expired!")
            print("Attempting to retreive a new GraphQL Bearer Token...")
            print()

            # Authenticate
            current_bearer_token = get_bearer_token(auth_json)

            print("New Token received: " + current_bearer_token)
            print()
            smp_response = perform_graphql_request(
                smp_query, auth_json["url"], headers={"Authorization": current_bearer_token})
        else:
            print("An error occured accessing the SM Platform!")
            print(e)
            exit(-1)

    print("Response from SM Platform was...")
    print()
    return smp_response