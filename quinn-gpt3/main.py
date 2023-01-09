import requests
import time
import random
import openai

from google.cloud import datastore

datastore_client = datastore.Client(namespace="mimi-robots")

def marvin_bot(request):
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
        evt = request_json['event']
        print(f"received event {evt}")

        if evt['type'] == 'message':
            time.sleep(5)
            msg = evt['text']
            if "bot_id" in evt and evt['bot_id'] != "BOT_ID_HERE":
                conv = get_conv()
                if conv and conv[-1]['user'] == "quinn":
                    print("I was last to speak.")
                    return "OK"
                print(f"Replying via GPT3 to {evt['bot_id']}")
                msg = gpt3_reply(evt['text'])
                update_conv(msg)
                return post_to_slack(msg)
            else:
                print("Message from myself.")
                return "OK"
    return f'OK'


def get_conv():
    # get all messages from datastore
    # delete all but largest two ids
    query = datastore_client.query(kind='Message')
    query_iter = query.fetch()
    entities = list(query_iter)
    entities = sorted(entities, key=lambda x: x['msg_id'])
    return entities


def update_conv(msg):
    # get all message ids from datastore
    # insert msg with largest id + 1
    # The kind for the new entity
    kind = "Message"

    query = datastore_client.query(kind='Message')
    query_iter = query.fetch()
    entities = list(query_iter)
    entities = sorted(entities, key=lambda x: x['msg_id'])
    keys = [x.key for x in entities]

    if len(keys) > 5:
        datastore_client.delete_multi(keys[:5])
    
    if len(keys) > 0:
        next_msg_id = entities[-1]['msg_id'] + 1
    else:
        next_msg_id = 0

    # Prepares the new entity
    entity = datastore.Entity(key=datastore_client.key(kind))
    entity["text"] = msg
    entity["msg_id"] = next_msg_id
    entity["user"] = "quinn"

    # Saves the entity
    datastore_client.put(entity)


def post_to_slack(message):
    webhook_url = 'WEBHOOK_URL_HERE'
    requests.post(webhook_url, json={"text": message})
    return "OK"


def gpt3_reply(message):
    conv = get_conv()

    conv_with_names = []
    for x in conv:
        msg = ""
        if x['user'] == "quinn":
            msg += "Quinn: "
        elif x['user'] == "alex":
            msg += "Alex: "
        else:
            raise Exception("Recorded message from unknown user.")
        msg += x['text']
        conv_with_names.append(msg)
        

    conv = "\n".join(conv_with_names)

    prompt=f"Quinn is chatting with Alex. Quinn is intelligent, funny, and sarcastic.\n\nAlex: Hi!\nQuinn: What's up?\n\n{conv}\nQuinn:"
    print(f"prompt: {prompt}")

    secret = access_secret_version("550391911750", "openai", "1")                
    openai.api_key = secret
    return openai.Completion.create(
        model="text-davinci-002",
        prompt=prompt,
        max_tokens=48,
        temperature=0.85,
        frequency_penalty=2.0,
        presence_penalty=1.0,
    )['choices'][0]['text']

def access_secret_version(project_id, secret_id, version_id):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    # Import the Secret Manager client library.
    from google.cloud import secretmanager
    import google_crc32c

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Verify payload checksum.
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        print("Data corruption detected.")
        return response
    
    payload = response.payload.data.decode("UTF-8")
    
    return payload
