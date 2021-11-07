import json


def sort_and_encode(dictionary: dict) -> bytes:
    return json.dumps(dictionary, separators=(',', ':'), sort_keys=True).encode('utf-8')
