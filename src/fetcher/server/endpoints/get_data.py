from typing import DefaultDict
from .PythonGraphQLRequestSample import perform_graphql_request, get_bearer_token
from werkzeug.exceptions import abort, BadRequest
from collections import defaultdict

def get_data(auth_json, query_json, check_auth = True):
    if query_json:
        equipment_name = query_json['Equipment']
        attribute_name = query_json['Attribute']
    else:
        raise  BadRequest(' No data in query_json')
    print("Requesting Data from CESMII Smart Manufacturing Platform...")
    print()

    smp_query = f'''
        query {{
                    typeToAttributeTypes(filter: {{displayName: {{equalTo: "{attribute_name}"}}}}) {{
                        id
                        dataType
                        maxValue
                        id
                        displayName
                        partOf {{
                        description
                        id
                            thingsByTypeId(filter:  {{displayName: {{equalTo: "{equipment_name}"}}}}) {{
                                displayName
                                id
                                updatedTimestamp
                                attributesByPartOfId(filter: {{displayName: {{equalTo: "{attribute_name}"}}}}) {{
                                    floatValue
                                    intValue
                                    id
                                }}
                            }}
                        }}
                    }}
            }}
    '''
    smp_response = ""

    # Get the first bearer token
    if auth_json:
        current_bearer_token = get_bearer_token(auth_json)
    else:
        raise BadRequest('auth_json object is None')

    try:
        # Try to request data with the current bearer token
        smp_response = perform_graphql_request(smp_query, auth_json["url"],  headers={"Authorization": current_bearer_token})
        print("SMP_RESPONSE: {}".format(smp_response))
    except Exception as e:
        print("get_data exception: {}".format(e))
        if "forbidden" in str(e).lower() or "unauthorized" in str(e).lower():
            print("Bearer Token expired!")
            print("Attempting to retrieve a new GraphQL Bearer Token...")
            print()

            # Authenticate
            current_bearer_token = get_bearer_token(auth_json)
            print("Got a token: '{}'".format(current_bearer_token))

            print("New Token received: " + current_bearer_token)
            print()

            # Re-try our data request, using the updated bearer token
            # TODO: This is a short-cut -- if this subsequent request fails, we'll crash. You should do a better job :-)
            smp_response = perform_graphql_request(
                smp_query, auth_json["url"], headers={"Authorization": current_bearer_token})
        else:
            print("An error occured accessing the SM Platform!")
            print(e)
            exit(-1)

    print("Response from SM Platform was...")
    print()
    return smp_response
