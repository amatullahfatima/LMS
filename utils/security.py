# utils/security.py
import hashlib

SALT = "dcccd_social_salt"

def hash_password(password: str) -> str:
    return hashlib.sha256((password + SALT).encode('utf-8')).hexdigest()

def check_password(hashed_password: str, user_password: str) -> bool:
    return hashed_password == hashlib.sha256((user_password + SALT).encode('utf-8')).hexdigest()
