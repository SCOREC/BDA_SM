from urllib import parse

def format_params(endpoint, params):
        parsed = parse.urlparse(endpoint)
        encoded_params = parse.urlencode(params)
        parsed = parsed._replace(query=encoded_params)
        return parse.urlunparse(parsed)
