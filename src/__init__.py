from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.tags.routes import tags_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from .errors import register_all_errors
from .middleware import register_middleware


# we use this decorator to determine which code would be run at the start of our app and which at the end of our app
# the ones above yield would be start at the start of our app(when our server starts) and the ones below yield would be start at the end of our app(when our server stops)

@asynccontextmanager
async def life_span(app: FastAPI):
    print("server is starting...")
        # since init_db() is Coroutine we've got to use await for it
        # what this line does is to run the init_db() function in which it will connect to our db and do our stuff
    # from src.db.models import Book
    # await init_db()
        # we are using lifespan event to make modification to our db
        # every time we create a table the lifespan event will run and create that table in our db
        # since we are using alembic now, server lifespan event is not needed anymore( init_db() is not needed anymore )

    yield
    print("server is shutting down...")


version = "v1"
app = FastAPI(
    title='Bookly',
    description='A rest API for a book review web service',
    version=version,
    lifespan= life_span,
    # terms_of_service=, # this gets url for the terms of service
    # docs_url=f"/api/{version}/docs",
    # redoc_url=f"/api/{version}/docs",
    contact={"email": "hos.ala81@gmail.com"},
    )



register_all_errors(app)
register_middleware(app)

# including our routes to our main file...
app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["users"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])
app.include_router(tags_router, prefix=f"/api/{version}/tags", tags=["tags"])
