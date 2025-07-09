from fastapi import APIRouter, status, HTTPException, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from .schemas import Book, BookUpdateModel, BookCreateModel, BookDetailModel
from src.db.main import get_session
from .service import BookService
from src.auth.dependecies import AccessTokenBearer, RoleChecker
from src.errors import BookNotFound





book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])



# when we add access_token_bearer Dependencies this endpoint will be a protected endpoint
# and when we send a req to this path it wouldn't return info unless we provide authorization header
# when passing our token we must provide our token in the form of bearer(Scheme) and then the token(Credentials) so we can receive the info



# this endpoint is made to get all the books from our server
@book_router.get('/', response_model = List[Book], dependencies=[Depends(role_checker)])
async def get_all_books(session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    books = await book_service.get_all_books(session)
    return books

# this endpoint returns all the book from a certain user which we specify by user_uid
@book_router.get('/user/{user_uid}', response_model = List[Book], dependencies=[Depends(role_checker)])
async def get_user_book_submissions(user_uid: str, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    books = await book_service.get_user_books(user_uid, session)
    return books


# this endpoint is made to create a new book on our server
@book_router.post('/', status_code=status.HTTP_201_CREATED, response_model= Book, dependencies=[Depends(role_checker)])
async def create_a_book(book_data: BookCreateModel, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)) -> Book:
    user_uid = token_details.get("user")["user_uid"] # get method allows us to access to a key
    new_book = await book_service.create_book(book_data, user_uid, session)
    return new_book



# this endpoint is made to fetch a book info by its id
@book_router.get('/{book_uid}', response_model=BookDetailModel, dependencies=[Depends(role_checker)])
async def get_book(book_uid: str, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)) -> dict:
    book = await book_service.get_book(book_uid, session)
    if book:
       return book
    else:
        raise BookNotFound()



# this endpoint is made to update a book information and by its id
@book_router.patch('/{book_uid}', response_model=Book, dependencies=[Depends(role_checker)])
async def update_book(book_uid: str, book_update_data: BookUpdateModel, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)) -> dict:
    updated_book = await book_service.update_book(book_uid, book_update_data, session)
    if updated_book:
        return updated_book
    else:
        raise BookNotFound()


# this endpoint is made to delete a book info by its id
@book_router.delete('/{book_uid}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(role_checker)])
async def delete_book(book_uid: str, session: AsyncSession = Depends(get_session), token_details: dict = Depends(access_token_bearer)):
    book_to_delete = await book_service.delete_book(book_uid, session)
    if book_to_delete is None:
        raise BookNotFound()
    else:
        return {}


