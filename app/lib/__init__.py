import re

from fastapi import Request


def natural_sort(l):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def get_remote_ip(request: Request):
    client_host = request.client.host
    return {"client_host": client_host}
