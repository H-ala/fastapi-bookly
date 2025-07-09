# here we create our exception classes which are going to be raised in case a specific error is raised from our app
# there are some General errors like not found or internal server
# there are some errors that are going to be raised because of user's actions like when they send request to endpoints which they don't have permission for it and etc

from typing import Any, Callable
from sqlalchemy.exc import SQLAlchemyError
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.requests import Request


# this is our base class for all our exceptions that are going to be raised
# this class is a subclass of default Exception class that python provides.
# we are defining all custom errors from BooklyException class
class BooklyException(Exception):
    """This is the base class for all bookly errors"""
    pass


class InvalidToken(BooklyException):
    """User has provided invalid or expired token"""
    pass

class RevokedToken(BooklyException):
    """User has provided a token that has been revoked"""
    pass

class AccessTokenRequired(BooklyException):
    """User has provided a refresh token when an access token is required"""
    pass

class RefreshTokenRequired(BooklyException):
    """User has provided an access token when a refresh token is required"""
    pass

class UserAlreadyExist(BooklyException):
    """User has provided an email for a user who exists during sign up"""
    pass

class InvalidCredentials(BooklyException):
    """User has provided wrong email or password during login"""
    pass

class InsufficientPermission(BooklyException):
    """User does not have the necessary permission to perform this action"""
    pass

class BookNotFound(BooklyException):
    """Book not found"""
    pass

class TagNotFound(BooklyException):
    """Tag not found"""
    pass

class TagAlreadyExists(BooklyException):
    """Tag already exists"""
    pass

class UserNotFound(BooklyException):
    """User not found"""
    pass

class AccountNotVerified(BooklyException):
    """Account not yet verified"""
    pass

# if we want to register our custom exceptions as ones that can be used by fastapi we need to create an exception handler
# exception handler is a function that fastapi will use to customize the responses that are going to be returned

# this function returns status code which is the status code we expect to return with the response once an exception has been raised
# we are going to return a massage or detail for that specific exception
# for detail we create initial_detail and it can be a str or a dict and etc. that's why we would set its type as Any
# we will also import Callable because we are returning a function which is the error handler(exception_handler) function
# we also need to provide the error_handler function's parameters in the Callable and it's output as well
# fastapi exception handlers take in two parameters 1.request obj 2.Exception obj and then it will return a JsonResponse
def create_exception_handler(status_code: int, initial_details: Any) -> Callable[[Request, Exception], JSONResponse]: # we expect this function to return a function
    async def exception_handler(request: Request, exc: BooklyException):
        # this function would be returned by  create_exception_handler function
        return JSONResponse(
            content=initial_details,
            status_code=status_code,
        )

    return exception_handler

def register_all_errors(app: FastAPI):
    # add_exception_handler method allows us to attach our custom error exception classes
    # this method takes in the exception class and then the function that's going to handle that exception which is create_exception_handler and this function takes in a bunch of parameters
    app.add_exception_handler(
        UserAlreadyExist,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_details={
                "message": "User with email already exists.",
                "error_code": "user_exists"
                # error_code further describes the errors and shows the client what exactly is happening. for example for frontend developers
            }
        )
    )
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_details={
                "message": "User not found",
                "error_code": "user_not_found"
            }
        )
    )
    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_details={
                "message": "Book not found",
                "error_code": "book_not_found"
            }
        )
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_details={
                "message": "Invalid email or password.",
                "error_code": "invalid_email_or_password"
            }
        )
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": "Token is invalid or expired",
                "resolution": "Please get new token",
                "error_code": "invalid_token"
            }
        )
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_details={
                "message": "Token is invalid or has been revoked",
                "resolution": "Please get new token",
                "error_code": "token_revoked"
            }
        )
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_needed"
            }
        )
    )

    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                "error_code": "refresh_token_needed"
            }
        )
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": "you are not allowed to perform this action",
                "error_code": "permission_denied"
            }
        )
    )
    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_details={
                "message": "this tag already exists",
                "error_code": "tag_exists"
            }
        )
    )
    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_details={
                "message": "this account has not been verified",
                "error_code": "account_not_verified",
                "resolution": "Please check your email for verification details"
            }
        )
    )

    # here we went to customize Internal Server error
    # we customize these error by using exception_handler on app decorator
    # it takes in status code(we can also provide error classes like what we already did)
    @app.exception_handler(500)
    async def internal_server_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            content={
                "message": "Oops.. sth went wrong in the app",
                "error_code": "server_error"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(SQLAlchemyError)
    async def database__error(request, exc):
        return JSONResponse(
            content={
                "message": "Oops! Something went wrong",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )