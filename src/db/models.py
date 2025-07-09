from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, date
from typing import Optional, List
import uuid


## User Model

# Instead of having id with type int we want to have a UID. This UID is going to be unique to any object that we would create in our db
# We want to use a postgresql specific type which is uuid. In order to do that we must use uuid module which is present in python.
# Once that's done we need to specify the exact way we want to store our uid in db. In order to do that we use Field function.
# In Field function we have to use the sqlalchemy column that's because we are going to access to the specific uid type in postgresql and that how we want it to be stored.
class User(SQLModel, table=True):
    __tablename__ = "users"
    # since we are using sa_column() which stands for sqlalchemy we must define the field as though we are defining a sqlalchemy field.
    # default is a new generated uid so that every field would be unique.
    uid: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4))
    username: str
    email: str
    first_name: str
    last_name: str
    # a field that specify the role of a user
    # since this is a new field we are adding to our table which already has data we must set a default value fot it so the blank spots would be filled
    # server_default argument allows us to provide a default value to the blank spots, hence the existing user will have the user role.
    role: str = Field(sa_column=Column(pg.VARCHAR, nullable=False, server_default="user"))
    is_verified: bool = Field(default=False)  # this one shows if the user has been verified or not
    password_hash: str = Field(
        exclude=True)  # what exclude does is to hide this field when returning response(it would not be serialized)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now()))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now()))

    # at books side we shall access to the user who is related to these books
    # we are going to get a list of books related to that user
    # now we must describe how sqlmodel or sqlalchemy is going to load this list of books
    # SQLModel by default use lazy loading, but it can be problematic in asyncDB APIs, hence we would use another way of loading --> sa_relationship_kwargs={"lazy":"selectin"}
    # this allows us to access the books that a user will have submitted
    books: List["Book"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})
    reviews: List["Review"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})


    # we are defining this function on the class above so as it would give us a string presentation of the Book object we have stored in our db
    def __repr__(self):
        return f'<User {self.uid}>'

## Tag Models

class BookTag(SQLModel, table=True):
    book_id: uuid.UUID = Field(default=None, foreign_key="books.uid", primary_key=True)
    tag_id: uuid.UUID = Field(default=None, foreign_key="tags.uid", primary_key=True)


class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(link_model=BookTag, back_populates="tags", sa_relationship_kwargs={"lazy": "selectin"})

    def __repr__(self) -> str:
        return f"<Tag {self.name}>"


## Book Model

# Instead of having id with type int we want to have a UID. This UID is going to be unique to any object that we would create in our db
# We want to use a postgresql specific type which is uuid. In order to do that we must use uuid module which is present in python.
# Once that's done we need to specify the exact way we want to store our uid in db. In order to do that we use Field function.
# In Field function we have to use the sqlalchemy column that's because we are going to access to the specific uid type in postgresql and that how we want it to be stored.
class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        # since we are using sa_column() which stands for sqlalchemy we must define the field as though we are defining a sqlalchemy field.
        # default is a new generated uid so that every field would be unique.
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    # here we are adding a foreign key to relate our books table to our users table
    # this user_id is going to be an optional field because it's going to be unnullable anyway and its type is uuid
    # in front of foreign_key we would write on of the fields of users table which we want it to relate to (tableName + filedName)
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    # we are defining these two last fields as timestamp from postgresql dialect
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))

    # after setting up relationship between tables, relationship attr makes it easy for us to access them using reverse relationship
    # this user field allows us to access the user who we have stored it's uid in user_uid field. we are going to access that via the ralationship function
    # ralationship function helps us use relationships to get those obj that are related to a certain obj such as the book obj
    # we are going to access that user table so we must use its model which is User
    # this field allows us to access the user who submitted this book
    user: Optional["User"] = Relationship(back_populates="books")
    # back_populates means in our user side we shall access all books that are related to that user and on our book side we shall access to the user who is related to this book


    reviews: List["Review"] = Relationship(back_populates="book", sa_relationship_kwargs={"lazy": "selectin"})

    tags: List[Tag] = Relationship(link_model=BookTag, back_populates="books", sa_relationship_kwargs={"lazy": "selectin"})

    # we are defining this function on the class above so as it would give us a string presentation of the Book object we have stored in our db
    # this is how we can visually see our User model
    def __repr__(self):
        # It returns an object of type book, but it's going to return it in a very readable format
        return f"<Book {self.username}>"


## Review Model

class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4))
    rating: int = Field(lt=6, gt=0) # lt(lower than), gt(greater than)
    review_text: str # this means this field is simply a string and it will not be nullable
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    book_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="books.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    # user attribute allows us to access the user who created the review
    user: Optional["User"] = Relationship(back_populates="reviews")
    book: Optional["Book"] = Relationship(back_populates="reviews")

    def __repr__(self): # this method returns a string representation of any object that we create out of this class
        return f"<Review for book {self.book_uid} by user {self.user_uid}>"


