from multiprocessing import AuthenticationError
from typing import DefaultDict
from .PythonGraphQLRequestSample import No_Request, perform_graphql_request, get_bearer_token
from werkzeug.exceptions import abort, BadRequest
from collections import defaultdict

def perform_get_equipment_data(auth_json, equipment_json, check_auth = True):
    try:
        equipment_name = equipment_json.get('Equipment')
        attribute_name = equipment_json.get('Attribute')
    except:
        raise BadRequest('Bad data in equipment section of JSON query')

    print("Requesting Data from CESMII Smart Manufacturing Platform...")

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
    
    try: # see if we have a token and try it.
        current_bearer_token = auth_json['bearer_token']
        smp_response = perform_graphql_request(smp_query,
            auth_json["url"],
            headers={"Authorization": current_bearer_token})
        print("Passed bearer token was good")
    except (No_Request, KeyError):
        try: # Looks like an invalid token. Try to get a good one
            current_bearer_token = get_bearer_token(auth_json)
            smp_response = perform_graphql_request(smp_query,
                auth_json["url"],
                headers={"Authorization": current_bearer_token})
            print("Got a good token")
        except AuthenticationError as err:
            raise BadRequest("SMIP could not issue JWT.")
        except No_Request as err:
            raise BadRequest("Could not retrieve data from SMIP. SMIP responded: {}".format(err))
    
    return smp_response
