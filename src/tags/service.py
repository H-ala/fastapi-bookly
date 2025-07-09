from anyio import wait_writable

from src.db.models import Tag
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import TagCreateModel, TagAddModel
from src.books.service import BookService
from fastapi import HTTPException, status
from sqlmodel import select, desc
from src.errors import TagNotFound, BookNotFound, TagAlreadyExists

book_service = BookService()


class TagService():

    async def get_tags(self, session: AsyncSession):
        """Get all tags"""
        statement = select(Tag).order_by(desc(Tag.created_at))
        result = await session.exec(statement)
        tags = result.all()
        return tags

    async def add_tag(self, tag_data: TagCreateModel, session: AsyncSession):
        """Create a new tag"""
        statement = select(Tag).where(Tag.name == tag_data.name)
        result = await session.exec(statement)
        tag = result.first()
        if tag:
            raise TagAlreadyExists()

        new_tag = Tag(name=tag_data.name)
        session.add(new_tag)
        await session.commit()
        return new_tag

    async def add_tags_to_book(self, book_uid: str, tag_data: TagAddModel, session: AsyncSession):
        """Add tags to a book"""
        book = await book_service.get_book(book_uid, session)
        if not book:
            raise BookNotFound()

        for tag_data in tag_data.tags:
            statement = select(Tag).where(Tag.name == tag_data.name)
            result = await session.exec(statement)
            tag = result.one_or_none() # this line return a tag if it exists in the db else it would return none
            if not tag:
                tag = Tag(name=tag_data.name) # if the tag was not in the db we would add it to the db
            book.tags.append(tag)

        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book



    async def get_tag_by_uid(self, uid: str, session: AsyncSession):
        """Get tag by uid"""
        statement = select(Tag).where(Tag.uid == uid)
        result = await session.exec(statement)
        tag = result.first()
        return tag



    async def update_tag(self, tag_uid: str, tag_update_data: TagCreateModel, session: AsyncSession):
        """Update a tag"""
        tag = await self.get_tag_by_uid(tag_uid, session)

        if not tag:
            raise TagNotFound()

        update_data_dict = tag_update_data.model_dump()
        for k, v in update_data_dict.items():
            setattr(tag, k, v)

            await session.commit()
            await session.refresh(tag)

        return tag


    async def delete_tag(self, tag_uid: str, session: AsyncSession):
        """Delete a tag"""
        tag = await self.get_tag_by_uid(tag_uid, session)
        if not tag:
            raise TagNotFound()

        await session.delete(tag)
        await session.commit()



