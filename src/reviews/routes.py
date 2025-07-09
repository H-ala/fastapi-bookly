from fastapi import APIRouter, Depends, status, HTTPException
from .service import ReviewService
from src.db.models import User
from src.reviews.schemas import ReviewCreateModel
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependecies import RoleChecker, get_current_user

review_Service = ReviewService()

review_router = APIRouter()  # this instance is going to have all routes that are basically related to reviews


admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))

# this endpoint will return all the reviews
@review_router.get("/", dependencies=[admin_role_checker])
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    reviews = await review_Service.get_all_reviews(session)
    return reviews


# this endpoint return a review by its uid
# when this endpoint depends on RoleChecker that means it also depends on AccessTokenBearer
@review_router.get("/{review_uid}", dependencies=[user_role_checker])
async def get_review_by_uid(review_uid: str, session: AsyncSession = Depends(get_session)):
    review = await review_Service.get_review_by_uid(review_uid, session)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review does not exist")
    return review


# this path will create a new review
@review_router.post('/book/{book_uid}', status_code=status.HTTP_201_CREATED, dependencies=[user_role_checker])
async def add_review_to_book(book_uid: str,
                             review_data: ReviewCreateModel,
                             current_user: User = Depends(get_current_user),
                             session: AsyncSession = Depends(get_session)):

    new_review = await review_Service.add_review_to_book(user_email=current_user.email, book_uid=book_uid, review_data=review_data, session=session)

    return new_review

# this endpoint will delete a review
@review_router.delete("/{review_uid}", dependencies=[user_role_checker], status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_uid: str, current_user = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await review_Service.delete_review_from_book(review_uid=review_uid, user_email=current_user.email ,session=session)
    return None