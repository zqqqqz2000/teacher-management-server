from hashlib import md5 as hash_md5


def md5(password: str) -> str:
    m = hash_md5()
    m.update(password.encode())
    return m.hexdigest()
