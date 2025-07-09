# HTTPBearer allows us to protect an endpoint and makes it only accessible if users provide theirs token(in the form of bearer and then token)
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from src.auth.utils import decode_token
from fastapi import Request, HTTPException, status, Depends
from src.db.redis import token_in_blocklist
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .service import UserService
from typing import List # to be more verbose and more specific we can use List from typing
from src.db.models import User
from src.errors import (
    InvalidToken, RefreshTokenRequired, AccessTokenRequired, InvalidToken, InsufficientPermission, AccountNotVerified
)

user_service = UserService()


# this class allow us to validate our access token
# this class is to create a dependency that shall be injected into every path handler that will require an access token to return the needed info
# this is the base class
class TokenBearer(HTTPBearer):
    # auto_error is an attr to this class that's going to determine the behaviour of this class when an error occurs
    # so when we have an error fastapi is going to return that error but in case we set that to False then fastapi would not return that error and instead returns None
    # so if an error occurs we are getting the Error in case auto_error is Tru and if we don't then it would be None
    # we will set it to True so we can get the real error that has happened
    def __init__(self, auto_error=True):
        super().__init__(
            auto_error=auto_error)  # this is going to call the init method of our parent class which is HTTPBearer


    # every time we want to create a python object from a class and we want that obj to act as sth like a function then we must use __call__ method
    # this method allows us to create these dependencies and then call them as functions(whoever has __call__ can be called as a function when creating a obj from that class)
    # call method is the main method that allows us to access our credentials and carry out whatever we need to do in forms of authorization
    # it gets the authorization header and then splits it in two parts, 1.scheme(bearer part of authorization header) 2.credentials(the token)
    # after that it checks whether we have provided those or not. if not it will raise HTTPException error if we have then it checks if the bearer is valid or not
    # if it is invalid it raise HTTPException error
    # if we want to add other checking we must overwrite this function and that's what we have done
    # it returns HTTPAuthorizationCredentials or None in case they are not received
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        # print(creds.scheme) # it returns bearer
        # print(creds.credentials) # it returns the token

        # let's authorize our users(check if our user is valid and providing a valid access token)

        token = creds.credentials
        token_data = decode_token(token)

        if not self.token_valid(token):
            raise InvalidToken()

        # here we check if the token is in the blocklist
        if await token_in_blocklist(token_data['jti']):
            raise InvalidToken()

        self.verify_token_data(token_data)  # here we beat one bird with two stones

        # instead of returning the token we will return the token data
        return token_data

    # now that we have access to our token we must decode it and find out whether it's valid or not
    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)  # this function returns None if our token is not valid
        # return True if token_data is not None else False
        return token_data is not None

    # this is a method that is accessed by the parent class but the other classes verify_token_data methods are going to override it
    # but in case they are not implemented we would raise NotImplementedError function meaning that if it failed to override, then throw that error and do what it says
    def verify_token_data(self, token_data):
        raise NotImplementedError("Please Override this method in child classes")


# this class is a child(sub) class of our TokenBearer
# this is where we're going to check if a valid access token is provided to an endpoint
class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        # here we check if token_data refresh attr is True then that will be marked as a refresh token
        # this func checks if a refersh token is sent to the token that requires an access token and then it's going to throw an error in case we provide refresh token instead of an acess token
        if token_data and token_data["refresh"]:  # if the token_data is not None and the token is refresh token raise an error
            raise AccessTokenRequired()


# this class checks if a valid refresh token is provided
# we define a new class that is going to help us create the  dependency for those endpoints that we shall need to access with a refresh token
class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        # here we check if token_data refresh attr is True then that will be marked as a refresh token
        # this func checks if a refresh token is sent to the token that requires an access token, and then it's going to throw an error in case we provide refresh token instead of an acess token
        if token_data and not token_data[
            "refresh"]:  # if the token_data is not None and the token is not refresh token raise an error
            raise RefreshTokenRequired()


# this is a dependency which gets the current logged in user
# this is going to take the token that is provided via the authorization headers
# we can inject into a dependency as many dependencies as we want but the problem is we must do in for only dependencies that we are going to use within routes
# if we inject a dependency into a class or a function that we are using outside routes that's not going to work
# here we inject session dependency to this class
# any checks for the token will be done by this dependency
async def get_current_user(token_details: dict = Depends(AccessTokenBearer()), session: AsyncSession = Depends(get_session)): # token_details is an obj of AccessTokenBearer class and is provided as a dependency in this function which will be used in our route handler
    # here we get the user email and use that email to get that user from our db
    user_email = token_details["user"]["email"]
    user = await user_service.get_user_by_email(user_email, session)
    return user


# this class is RoleChecker dependency
# if we want to create an obj from this class and call it as a function then we must define __call__ function in it
class RoleChecker:

    def __init__(self, allowed_roles: List[str]) -> None: # each obj we make from this class is going to take in a list of roles
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if not current_user.is_verified: # this means if the user is_verified field is False then raise an error since they are not allowed to do anything
            raise AccountNotVerified()
        if not current_user.role in self.allowed_roles: # checking if a role has been provided to the endpoint
            raise InsufficientPermission()


