from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import ReviewCreateModel
from fastapi import HTTPException, status
import logging
from sqlmodel import select, desc

book_service = BookService()
user_service = UserService()

class ReviewService:
    async def add_review_to_book(self, user_email: str, book_uid: str, review_data: ReviewCreateModel, session: AsyncSession):
        try:
            # first we would fetch the book that a user wants to submit a review to it
            book = await book_service.get_book(book_uid=book_uid, session=session)
            if not book:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found") # if that book does not exist we would raise a error

            # after that we would fetch the user who wants to submit a review
            user = await user_service.get_user_by_email(email=user_email, session=session)
            if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found") # if that user does not exist we would raise a error

            # now that we have both user and book let's create a review and associate it with these two obj

            review_data_dict = review_data.model_dump()  # this line turns our json to dictionary
            new_review = Review(**review_data_dict) # new review is an instance of review model


            new_review.user = user # this line fills the user_uid field
            new_review.book = book # this line fills the book_uid field

            session.add(new_review)
            await session.commit()

            return new_review

        except Exception as e:
            logging.exception(e) # this is one way to get the log of an exception and understand where it is coming from
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Oops... sth went wrong")



    async def get_all_reviews(self, session: AsyncSession):
        # this function returns all the books
        statement = select(Review).order_by(desc(Review.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_review_by_uid(self, review_uid: str, session: AsyncSession):
        statement = select(Review).where(Review.uid == review_uid)
        result = await session.exec(statement)
        review = result.first()
        return review if review else None


    async def delete_review_from_book(self, review_uid: str, user_email: str ,session: AsyncSession):
        user = await user_service.get_user_by_email(email=user_email, session=session)
        review = await self.get_review_by_uid(review_uid=review_uid, session=session)
        if not review or (review.user != user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="cannot delete review")

        await session.delete(review)
        await session.commit()

