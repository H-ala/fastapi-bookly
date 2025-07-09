from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from src.db.models import Book
from sqlmodel import select, desc
from datetime import datetime

# Service class has all the logic for creating crud, so the moment we need to carry out the crud operations the only thing we should do is to use Service class's methods
# we use this class so we can separate our crud codes from our route handlers and make the codes cleaner

# session is a medium by sqlmodel and sqlalchemy so we can have access to our db and carry out transaction on it.
class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.user_uid == user_uid).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()


    async def get_book(self, book_uid: str,  session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book if book is not None else None


    async def create_book(self, book_data: BookCreateModel, user_uid: str, session: AsyncSession):
        book_data_dict = book_data.model_dump() # this line turns our json to dictionary
        new_book = Book(**book_data_dict) # this line unpacks our book_data_dictionary. it will create a new_book obj with attrs it gets from the book_data_dict
        # strptime is a function that gets a string and turns it to a date type
        new_book.published_date = datetime.strptime(book_data_dict["published_date"], "%Y-%m-%d")
        # here we make the relationship between books and users
        new_book.user_uid = user_uid
        session.add(new_book)
        await session.commit()
        return new_book


    async def update_book(self, book_uid: str, update_data: BookUpdateModel, session: AsyncSession):
        book_to_update = await self.get_book(book_uid, session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump()
            for k, v in update_data_dict.items():
                # the setattr func will get an obj such as book_to_update obj, and then it will update it base on the keys and its respective value
                setattr(book_to_update, k,v)
            await session.commit()
            return book_to_update
        else:
            return None


    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book(book_uid, session)
        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return {"done"}
        else:
            return None

