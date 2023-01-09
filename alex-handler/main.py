import requests

def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()

    if request_json and 'event' in request_json:
        print("Event received")
        second_function = 'BOT_URL_HERE'
        try:
            requests.post(second_function, json=request_json, timeout=1)
        except Exception as e:
            print(e)
        print("Finished handling event")
        return "OK"
    elif request_json and 'challenge' in request_json:
        print("challenge received")
        return request_json['challenge']

    return "OK"
