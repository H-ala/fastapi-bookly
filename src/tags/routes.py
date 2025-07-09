from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from .schemas import TagCreateModel, TagModel, TagAddModel
from .service import TagService
from src.auth.dependecies import RoleChecker
from typing import List
from src.books.schemas import Book

tags_router = APIRouter()
tag_service = TagService()
user_role_checker = RoleChecker(["user", "admin"])


# this endpoint return all tags
@tags_router.get("/", dependencies=[Depends(user_role_checker)], response_model=List[TagModel])
async def get_all_tags(session: AsyncSession = Depends(get_session)):
    tags = await tag_service.get_tags(session)
    return tags


# this endpoint create a new tag
@tags_router.post("/", response_model=TagModel, status_code=status.HTTP_201_CREATED,
                  dependencies=[Depends(user_role_checker)])
async def add_tag(tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)):
    tag_added = await tag_service.add_tag(tag_data, session)
    return tag_added


# this endpoint add tags to a book by its uid
@tags_router.post("/book/{book_uid}/tags", dependencies=[Depends(user_role_checker)], response_model=Book)
async def add_tags_to_book(book_uid: str, tag_data: TagAddModel, session: AsyncSession = Depends(get_session)):
    book_with_tag = await tag_service.add_tags_to_book(book_uid, tag_data, session)
    return book_with_tag


@tags_router.put("/{tag_uid}", dependencies=[Depends(user_role_checker)], response_model=TagModel)
async def update_tag(tag_uid: str, tag_update_data: TagCreateModel, session: AsyncSession = Depends(get_session)):
    updated_tag = await tag_service.update_tag(tag_uid, tag_update_data, session)
    return updated_tag

# this endpoint will delete a tag
@tags_router.delete("/{tag_uid}", dependencies=[Depends(user_role_checker)], status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_uid: str, session: AsyncSession = Depends(get_session)):
    deleted_tag = await tag_service.delete_tag(tag_uid, session)
    return deleted_tag
