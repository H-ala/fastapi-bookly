from asyncpg.pgproto.pgproto import timedelta
from passlib.context import CryptContext
from datetime import datetime, timedelta
from src.config import Config
import jwt
import uuid
import logging
from itsdangerous import URLSafeTimedSerializer

# URLSafeTimedSerializer takes in a str and then creates a token into it, and we can set the time the data has been signed
# for example we create a token and we want to check if it has been signed and how much it has been passed around, in that case we can use this module

# HASHing
# we will hash our password with the help of CryptoContext func and bcrypt algorithm
passwd_context = CryptContext(schemes=["bcrypt"])


# this function is going to take the user password and generate a hash for it and then returns that
def generate_passwd_hash(password: str) -> str:
    hash = passwd_context.hash(password)
    return hash


# in this funciton we provide the pass and hashed_pass, and it would tell us if the pass is correct or not by returning True or False
def verify_passwd_hash(password: str, hashed_password: str) -> bool:
    return passwd_context.verify(password, hashed_password)


# JWT

ACCESS_TOKEN_EXPIRY = 3600  # token would be valid for 3600 seconds and after 3600 seconds, the user has to enter the system again or sends refresh token to take another token


# we are going to define two functions
# the first function is to create and encode our token. it requires user's data in dict type, and expiry of the token which is timedelta type
# this function is going to create both access token and refresh token
# refresh tokens are longer than access tokens. refresh tokens will be used to get more tokens in case our access tokens are expired
def create_access_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    # payload is the data or claim  we want to encode as a json obj within our token
    payload = {}
    payload["user"] = user_data
    payload["exp"] = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
    # we need to provide an uid for each token that is being created
    # jti stands for jwt id
    # since uuid.uuid4 is an uuid type we must serialize it into  a json serializable format by changing its type to str
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    # inside encode function we are sending arguments that are required to create an access token
    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET, # key is the secret key that PyJWT use to sign our token(we'll set this up inside our environment variables)
        algorithm=Config.JWT_ALGORITHM,  # algorithm is the way PyJWT encode our token
    )

    return token

# the second function is used to decode the token we created
# this function will return the data contained in the token as a dictionary
# there are a lot of chances that we are going to land in errors when we decode the token, errors like token being expired or the signature verification failing and so on
# so we would use try & except method for it
def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return token_data
    # in case you couldn't decode the token, except the PyJWT specific errors
    except jwt.PyJWTError as e:
        logging.exception(e) # we log the error
        return None


# to create a token we need to create an instance of URLSafeTimeSerializer class
# it takes in the key which is the secret key that is used to sign our data. we keep it to the same value as our JWT secret key
serializer = URLSafeTimedSerializer(secret_key=Config.JWT_SECRET, salt="email-verification") # we can call salt anything we want
def create_url_safe_token(data: dict) -> str:
    """create url safe token"""
    # now that we have created this serializer we must use it to sign the data that we've sent within this function
    # dumps allow us to get a value and serialize it into a string that is going to be like token
    token = serializer.dumps(data)

    return token


def decode_url_safe_token(token: str) -> dict:
    """decode url safe token"""
    # we can encounter a lot of errors such as when data has been tempered with or when it has a bad signature and so on. that's why we would use try except
    try:
        token_data = serializer.loads(token) # this is the opposite of dump method, and it will return the data which is inside the token
        return token_data
    except Exception as e:
        logging.error(str(e))