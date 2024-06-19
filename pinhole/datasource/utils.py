def str2hexstr(body: str) -> str:
    return body.encode('utf8').hex()


def hexstr2str(body: str) -> str:
    return bytes.fromhex(body).decode('utf8')
