# here is the codes to connect to our db

from sqlmodel import create_engine, text, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine
from src.config import Config
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker
from src.db.models import Book

# since we are using an async DB API, therefor, we need to create an async engine(AsyncEngine)
async_engine = AsyncEngine(
    create_engine(url= Config.DATABASE_URL) # echo=True will show the DB logs in our terminal so as we would have a better understanding of what's going on
)

# this function will be used in the main(__init__.py) file, in the life_span function so as when the server starts we would hava a connection with the database(at the start of our app).
# this function will allow us to build a connection to our database and keep that connection for as long as our application is running
async def init_db():
    async with async_engine.begin() as conn: # the connection is to db is made
        await conn.run_sync(SQLModel.metadata.create_all) # we are using run_sync() which helps us to run synchronous code with our connection object



# this function is responsible for returning our session we'll be using across all route handlers
# the return type of this function is of AsyncSession
async def get_session() -> AsyncSession:
    # when we want to create a session we need a Session class and we'll be using sqlalchemy sessionmaker for that
    # we are using sqlmodel AsyncSession and for that we need sessionmaker as it helps us to define any class that we want to use for creating a session
    # Session is a class that is going to be created from our sessionmaker
    # when we create a Session we need to bind it to an engine so that we can access our db
    # expire_on_commit= False allows us to use our session obj even after commiting transaction to our database
    Session = sessionmaker(bind= async_engine, class_= AsyncSession, expire_on_commit= False)
    async with Session() as session:
        yield session
# and now we craeted our first dependency