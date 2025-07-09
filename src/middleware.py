from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time
import logging

# uvicorn.access is the one that logs some unnecessary things when we start our server
logger = logging.getLogger("uvicorn.access")
logger.disabled = True # this line will prevent those log to get written on our terminal



def register_middleware(app: FastAPI):

    # for using middleware, we would use middleware decorator which takes the type of middleware we want to create like http or web sockets or ...
    # since we are dealing with a http server we would use http
    @app.middleware("http")
    # the following function would run within our middleware
    # every middleware function takes two parameters
    # the first one is the request of type Request which we want to pass to that middleware before we pass it on to the route handler
    # the second one is call_next which is the specific route handler or any other middleware that will be needed to process that specific request
    # the second one is call_next which is another middleware that's going to be registered on our app as well as any route handler that we've defined

    async def custom_logging(request: Request, call_next):
        start_time = time.time() # this variable store the current time at the moment

        # now we can calculate the processing time for this request
        # we must do what we want before the request is done(passed to the route handler)


        # to get our response we need to use call_next function with the current request as an argument
        # it will go ahead and set up our response obj
        response = await call_next(request) # after this line request ends and it will pass to the route handler


        processing_time = time.time() - start_time
        # we want to get the request time and some other things. they all can be accessed via request obj
        message = f"{request.client.host}:{request.client.port} - {request.method} - {request.url.path} - {response.status_code} completed after {processing_time} seconds"
        print(message)

        # when we are done processing the request with our middleware, we would return the response
        return response


    # @app.middleware("http")
    # async def authorization(request: Request, call_next):
    #     # when we define middleware on our app instance it will work on all the endpoints we have
    #     # we are going to check all the request to see if the user has an authorization header
    #     # we can check it out in request.headers
    #
    #     if "Authorization" not in request.headers: # if this is True, user is not authenticated
    #         # when using middleware we cannot raise an HTTPException inside middleware. it will be raised as an exception but won't be returned as response
    #         # if we want to return some kind of response we must return it inside the response  with the help of JSONResponse class
    #         return JSONResponse(
    #             content={"message": "Not Authenticated",
    #                      "resolution": "Please provide the right credentials to proceed"},
    #             status_code=status.HTTP_401_UNAUTHORIZED
    #         )
    #
    #     response = await call_next(request)
    #     return response




    # we can check CORSMiddleware class to see which argument it takes and what we have access to
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True) # * means we are allowing all things that are related to that thing

     # trusted host set the host header and will guard against HTTP Host Header attacks
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])


    # this is how we set up a custom middleware and this can be in any asgi middleware that we want to use in our app(import it and add it like that)
